# -*- coding: utf-8 -*-
"""Extract text from a PDF.

Two modes:
  --check : report page count and how much native text the PDF contains
            (to decide markitdown vs OCR). No OCR performed.
  default : if the PDF has no/low text layer, render each page with PyMuPDF
            and OCR it, writing page-delimited text.

Engines (--engine):
  tesseract (default)
      Fast (~1-2 s/page), CPU only, one traineddata per language, plain text.
      Needs Tesseract-OCR -> run scripts/setup_env.ps1 first.

  uocr
      Unlimited-OCR v1 (3B MoE VLM) as GGUF via llama.cpp.
      Slow (~10-15 s/page) but keeps tables/headings as markdown and reads
      multilingual scans with no per-language data. Vision runs on Vulkan or
      CPU. Needs the GGUF models + a llama.cpp build -> setup_env.ps1 -Engine uocr.

Examples:
  conda run -n pdf-ocr python ocr_pdf.py --check doc.pdf
  conda run -n pdf-ocr python ocr_pdf.py doc.pdf doc.txt -l vie
  conda run -n pdf-ocr python ocr_pdf.py doc.pdf -l eng+vie --dpi 400
  conda run -n pdf-ocr python ocr_pdf.py scan.pdf -e uocr
  conda run -n pdf-ocr python ocr_pdf.py scan.pdf -e uocr --keep-boxes
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pymupdf

TESSDATA = os.path.join(os.path.expanduser("~"), ".tessdata")

# --- Unlimited-OCR (llama.cpp) layout ------------------------------------
UOCR_HOME = os.path.join(os.path.expanduser("~"), ".pdf-extract")
UOCR_MODEL = os.path.join(UOCR_HOME, "models", "Unlimited-OCR-Q4_K_M.gguf")
UOCR_MMPROJ = os.path.join(UOCR_HOME, "models", "mmproj-Unlimited-OCR-F16.gguf")
UOCR_LLAMA = os.path.join(UOCR_HOME, "llama", "llama-mtmd-cli.exe")

# Known-good decode settings for this model. The DRY sampler is required:
# without it dense pages fall into repetition loops and never terminate.
UOCR_SAMPLER = [
    "--chat-template", "deepseek-ocr",
    "--temp", "0",
    "--flash-attn", "off",
    "--no-warmup",
    "--dry-multiplier", "0.8",
    "--dry-base", "1.75",
    "--dry-allowed-length", "35",
    "--dry-penalty-last-n", "128",
    "--dry-sequence-breaker", "none",
]

DET_RE = re.compile(r"<\|det\|>.*?<\|/det\|>", re.S)


def find_tesseract():
    for cand in (os.environ.get("TESSERACT"),
                 shutil.which("tesseract"),
                 r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                 r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"):
        if cand and os.path.exists(cand):
            return cand
    return None


def tessdata_prefix(lang):
    """Return ~/.tessdata if it holds every requested language, else None."""
    langs = lang.split("+")
    if all(os.path.exists(os.path.join(TESSDATA, l + ".traineddata")) for l in langs):
        return TESSDATA
    return None


def find_uocr_binary():
    for cand in (os.environ.get("UOCR_LLAMA"), UOCR_LLAMA,
                 shutil.which("llama-mtmd-cli")):
        if cand and os.path.exists(cand):
            return cand
    return None


def native_text_len(doc):
    return sum(len(p.get_text() or "") for p in doc)


def ocr_tesseract(png, tess, lang, env):
    r = subprocess.run([tess, png, "stdout", "-l", lang], capture_output=True, env=env)
    return r.stdout.decode("utf-8", "replace")


def ocr_uocr(png, exe, model, mmproj, prompt, max_tokens, ngl, keep_boxes):
    cmd = [exe, "-m", model, "--mmproj", mmproj, "--image", png,
           "-p", prompt, "-n", str(max_tokens), "-c", "16384",
           "-ngl", str(ngl)] + UOCR_SAMPLER
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip().splitlines()
        tail = err[-3:] if err else ["(no stderr)"]
        sys.exit("uocr failed (exit %d):\n  %s" % (r.returncode, "\n  ".join(tail)))

    txt = r.stdout.decode("utf-8", "replace")
    txt = txt.replace("<|end|>", "")
    if not keep_boxes:
        txt = DET_RE.sub("", txt)
    return txt.strip() + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("out", nargs="?", help="output .txt (default <pdf>.ocr.txt)")
    ap.add_argument("-e", "--engine", choices=("tesseract", "uocr"), default="tesseract",
                    help="OCR backend (default tesseract)")
    ap.add_argument("-l", "--lang", default="eng",
                    help="Tesseract language(s), e.g. eng, vie, eng+vie (default eng)")
    ap.add_argument("--dpi", type=int, default=None,
                    help="render DPI (default 300 for tesseract, 200 for uocr); "
                         "raise to 300+ for small print")
    ap.add_argument("--check", action="store_true",
                    help="only report page count and native-text size, then exit")
    ap.add_argument("--prompt", default="document parsing.",
                    help="uocr prompt (default 'document parsing.'); "
                         "'Free OCR.' gives plain text without structure")
    ap.add_argument("--max-tokens", type=int, default=8192,
                    help="uocr output cap per page (default 8192)")
    ap.add_argument("--ngl", type=int, default=99,
                    help="uocr GPU layers, 0 = CPU only (default 99)")
    ap.add_argument("--keep-boxes", action="store_true",
                    help="uocr: keep <|det|>label [x,y,x,y]<|/det|> layout tags")
    ap.add_argument("--model", default=UOCR_MODEL, help="uocr model .gguf")
    ap.add_argument("--mmproj", default=UOCR_MMPROJ, help="uocr mmproj .gguf")
    a = ap.parse_args()

    if not os.path.exists(a.pdf):
        sys.exit("file not found: %s" % a.pdf)

    doc = pymupdf.open(a.pdf)
    chars = native_text_len(doc)

    if a.check:
        print("pages            : %d" % doc.page_count)
        print("native text chars: %d" % chars)
        print("avg chars/page   : %.1f" % (chars / max(doc.page_count, 1)))
        print("verdict          : %s" %
              ("text layer present -> use markitdown"
               if chars / max(doc.page_count, 1) > 200 else
               "little/no text -> OCR likely needed"))
        return

    env = dict(os.environ)
    tess = exe = None
    model = a.model
    mmproj = a.mmproj

    if a.engine == "tesseract":
        tess = find_tesseract()
        if not tess:
            sys.exit("tesseract not found; run scripts/setup_env.ps1 or set %TESSERACT%")
        prefix = tessdata_prefix(a.lang)
        if prefix:
            env["TESSDATA_PREFIX"] = prefix
    else:
        exe = find_uocr_binary()
        if not exe:
            sys.exit("llama-mtmd-cli not found; run: pwsh -File scripts/setup_env.ps1 -Engine uocr")
        for label, path in (("model", model), ("mmproj", mmproj)):
            if not os.path.exists(path):
                sys.exit("uocr %s missing: %s\nrun: pwsh -File scripts/setup_env.ps1 -Engine uocr"
                         % (label, path))

    out = a.out or (os.path.splitext(a.pdf)[0] + ".ocr.txt")
    dpi = a.dpi or (300 if a.engine == "tesseract" else 200)

    tmpdir = tempfile.mkdtemp(prefix="pdf_extract_")
    parts = []
    n = doc.page_count
    for i in range(n):
        pix = doc.load_page(i).get_pixmap(dpi=dpi)
        png = os.path.join(tmpdir, "pg%04d.png" % (i + 1))
        pix.save(png)
        if a.engine == "tesseract":
            txt = ocr_tesseract(png, tess, a.lang, env)
        else:
            txt = ocr_uocr(png, exe, model, mmproj, a.prompt,
                           a.max_tokens, a.ngl, a.keep_boxes)
        parts.append("===== PAGE %d =====" % (i + 1))
        parts.append(txt)
        print("page %d/%d" % (i + 1, n), flush=True)

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("wrote %s (%d chars)" % (out, sum(len(p) for p in parts)))


if __name__ == "__main__":
    main()

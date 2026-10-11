# -*- coding: utf-8 -*-
"""Extract text from a PDF.

Two modes:
  --check : report page count and how much native text the PDF contains
            (to decide markitdown vs OCR). No OCR performed.
  default : if the PDF has no/low text layer, render each page with PyMuPDF
            and OCR it with Tesseract, writing page-delimited text.

Requires (for OCR): PyMuPDF + Tesseract-OCR + language data
  -> run scripts/setup_env.ps1 first, then invoke with:
     conda run -n pdf-ocr python ocr_pdf.py <in.pdf> [out.txt] [-l lang]

Examples:
  conda run -n pdf-ocr python ocr_pdf.py --check doc.pdf
  conda run -n pdf-ocr python ocr_pdf.py doc.pdf doc.txt -l vie
  conda run -n pdf-ocr python ocr_pdf.py doc.pdf -l eng+vie --dpi 400
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import pymupdf

TESSDATA = os.path.join(os.path.expanduser("~"), ".tessdata")


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


def native_text_len(doc):
    return sum(len(p.get_text() or "") for p in doc)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("out", nargs="?", help="output .txt (default <pdf>.ocr.txt)")
    ap.add_argument("-l", "--lang", default="eng",
                    help="Tesseract language(s), e.g. eng, vie, eng+vie (default eng)")
    ap.add_argument("--dpi", type=int, default=300, help="render DPI (default 300)")
    ap.add_argument("--check", action="store_true",
                    help="only report page count and native-text size, then exit")
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

    tess = find_tesseract()
    if not tess:
        sys.exit("tesseract not found; run scripts/setup_env.ps1 or set %TESSERACT%")

    out = a.out or (os.path.splitext(a.pdf)[0] + ".ocr.txt")
    env = dict(os.environ)
    prefix = tessdata_prefix(a.lang)
    if prefix:
        env["TESSDATA_PREFIX"] = prefix

    tmpdir = tempfile.mkdtemp(prefix="pdf_extract_")
    parts = []
    n = doc.page_count
    for i in range(n):
        pix = doc.load_page(i).get_pixmap(dpi=a.dpi)
        png = os.path.join(tmpdir, "pg%04d.png" % (i + 1))
        pix.save(png)
        r = subprocess.run([tess, png, "stdout", "-l", a.lang],
                           capture_output=True, env=env)
        txt = r.stdout.decode("utf-8", "replace")
        parts.append("===== PAGE %d =====" % (i + 1))
        parts.append(txt)
        print("page %d/%d" % (i + 1, n), flush=True)

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("wrote %s (%d chars)" % (out, sum(len(p) for p in parts)))


if __name__ == "__main__":
    main()

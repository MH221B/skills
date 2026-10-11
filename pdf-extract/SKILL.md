---
name: pdf-extract
description: Get text out of PDFs and other documents by trying markitdown first and falling back to Tesseract OCR when a PDF is image-only/scanned. Use when reading, parsing, extracting, or searching PDF content; when markitdown returns nothing or garbled output; when a PDF "has no text" / is a scan; or when preparing a file for downstream work (summarize, search, translate, QA, datasets, re-formatting).
---

# PDF / document text extraction

Two-tier approach. **Always try markitdown first.** Only OCR when the PDF has no real text layer (pages are just embedded images).

## 1. Try markitdown first (no setup needed)

Call the markitdown MCP tool with a `file:`, `http(s):` or `data:` URI. It handles text PDFs, Office docs, HTML, images, and more:

```
tools.markitdown.convert_to_markdown({ uri: "file:///C:/path/doc.pdf" })
```

Judge the result:
- **Readable text** (roughly > 200 chars per page) → done, use it.
- **Empty, `null`, or tiny/garbled output** → the PDF is almost certainly scanned / image-only. Continue to step 2.

Spot-check a suspicious file (page count + extractable text, no OCR run):

```
conda run -n pdf-ocr python scripts/ocr_pdf.py --check "C:\path\doc.pdf"
```

## 2. Fallback: OCR with Tesseract

Ensure the toolchain exists. This is idempotent and safe to re-run:

```powershell
pwsh -File scripts/setup_env.ps1                 # conda env + Tesseract; English (bundled, no download)
pwsh -File scripts/setup_env.ps1 -Langs eng,vie  # add languages only when a document needs them
```

It will, only if missing: create the conda env `pdf-ocr` (Python + PyMuPDF), install Tesseract-OCR via winget, and download the requested `*.traineddata` files to `~/.tessdata`.

Then render each page and OCR it:

```powershell
conda run -n pdf-ocr python scripts/ocr_pdf.py "C:\path\doc.pdf" "C:\path\doc.txt" -l vie
```

- `-l` = Tesseract language(s), default `eng` (e.g. `vie`, `eng+vie`).
- `--dpi` default `300` (raise for small print, lower for speed).
- Output is page-delimited: `===== PAGE n =====`.

## 3. Use the text

Feed the extracted text into the actual task (summarise, search, translate, QA, build a dataset, re-format, etc.). Treat OCR output as **lossy** — expect minor character errors, especially in numbers and diacritics.

## Gotchas

- Never skip markitdown: it is exact and fast; OCR is slow (~1–3 s/page) and imperfect.
- Some scans carry a bad OCR text layer, so markitdown returns plausible-but-garbled text. If it reads wrong, ignore it and re-OCR with the correct `-l` language.
- Match the language code to the document; English-only OCR on non-English text produces noise.
- See [REFERENCE.md](REFERENCE.md) for setup internals, language list, and troubleshooting.

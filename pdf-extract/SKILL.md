---
name: pdf-extract
description: Get text out of PDFs and other documents by trying markitdown first, falling back to Tesseract OCR when a PDF is image-only/scanned, and escalating to Unlimited-OCR (vision model, keeps tables/layout, reads multilingual scans) when Tesseract garbles or returns nothing. Use when reading, parsing, extracting, or searching PDF content; when markitdown returns nothing or garbled output; when a PDF "has no text" / is a scan; or when preparing a file for downstream work (summarize, search, translate, QA, datasets, re-formatting).
---

# PDF / document text extraction

Three tiers. **Always try markitdown first.** Only OCR when the PDF has no real text layer (pages are just embedded images).

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

## 2. Standard OCR: Tesseract (fast)

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

## 3. Escalation: Unlimited-OCR (slow, much better on hard scans)

Use when Tesseract output is **wrong rather than merely imperfect**: mangled diacritics, dropped table columns, repeated lines, merged columns, or `Empty page!!`. This tier runs a 3B vision model through llama.cpp, so it keeps tables and headings as markdown and reads non-Latin text with no per-language data.

### Do not install this tier unless the user explicitly asks

It is a ~3.5 GB download and 10–40× slower than Tesseract. Never set it up on your own initiative, and never as a "just in case" step — if the user only wants the document read, keep using Tesseract and say why the text is imperfect.

If they ask for it, **ask one question first**:

> The model files are public, so a Hugging Face token is optional — it mainly avoids anonymous rate limits. Do you have one you want used for the download?

Then:

- **`HF_TOKEN` already set in their environment** → run the setup below; it is picked up automatically.
- **They want to supply one** → have them set it themselves (`$env:HF_TOKEN = 'hf_...'`), or start a fresh shell with it. Do not echo the token back, and do not put it on a command line — it ends up in process listings and logs.
- **No token** → run the setup normally. Anonymous download works.

```powershell
pwsh -File scripts/setup_env.ps1 -Engine uocr
```

Run it:

```powershell
conda run -n pdf-ocr python scripts/ocr_pdf.py "C:\path\doc.pdf" -e uocr
conda run -n pdf-ocr python scripts/ocr_pdf.py "C:\path\doc.pdf" -e uocr --dpi 300   # small print
```

- Output stays page-delimited (`===== PAGE n =====`) but the content is **markdown**, including `<table>` markup. Layout coordinates are stripped; add `--keep-boxes` to keep them.
- `--dpi` defaults to `200` here (≈12 s/page on a clean A4). At `300` it is ≈60 s/page on dense pages — needed for small print, otherwise too slow.
- Run long documents **in the background**; a 30-page scan is minutes, not seconds.
- `--prompt "Free OCR."` gives plain text with no structure if markdown gets in the way.

## 4. Use the text

Feed the extracted text into the actual task (summarise, search, translate, QA, build a dataset, re-format, etc.). Treat OCR output as **lossy** — expect minor character errors, especially in numbers and diacritics.

## Gotchas

- Never skip markitdown: it is exact and fast; OCR is slow (Tesseract ~1–3 s/page, Unlimited-OCR ~12–60 s/page) and imperfect.
- Some scans carry a bad OCR text layer, so markitdown returns plausible-but-garbled text. If it reads wrong, ignore it and re-OCR.
- Match the language code to the document; English-only Tesseract on non-English text produces noise. Unlimited-OCR does not need language selection.
- Unlimited-OCR is a *repair* tier, not a default. It is 10–40× slower than Tesseract, only worth it when Tesseract is failing, and must not be installed unless the user explicitly asks.
- See [REFERENCE.md](REFERENCE.md) for setup internals, language list, and troubleshooting.

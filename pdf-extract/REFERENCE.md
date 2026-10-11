# pdf-extract — reference

## Why two tiers?

- **markitdown** reads documents that already contain a text layer. It is exact, instant, and needs no software install. It is the default for every file.
- **OCR** is only needed when a PDF is a *scan*: each page is an embedded raster image with no text. markitdown (and any text extractor) returns nothing useful for these.

Decision rule: **markitdown result looks good → use it; empty/`null`/tiny/garbled → OCR.**

## Detecting a scanned / image-only PDF

Quick check (no OCR performed):

```powershell
conda run -n pdf-ocr python scripts/ocr_pdf.py --check "C:\path\doc.pdf"
```

Output shows page count and total extractable-text characters. Near-zero chars over many pages = image-only.

Other signals:
- markitdown returns `null` or a 0–4 char string.
- `pypdf`: `len(list(page.images)) > 0` on every page and `page.extract_text()` is empty.
- The file is large (multi-MB) relative to its page count.

## What `setup_env.ps1` does (idempotent)

1. **conda env `pdf-ocr`** — created with Python 3.12 if absent; then `pip install pymupdf` (page rendering). PyMuPDF renders reliably regardless of how the page image is encoded (JPEG / TIFF / CCITT / JBIG2).
2. **Tesseract-OCR** — if `%ProgramFiles%\Tesseract-OCR\tesseract.exe` is missing, installs `UB-Mannheim.TesseractOCR` via winget.
3. **Language data** — default is `eng`, which ships with the installer (no download). Additional languages are downloaded (from `tessdata_best`) into `~/.tessdata` only when requested, and only if not already present or bundled with the installer. Add languages only when a document actually needs them, e.g. `-Langs eng,vie`.

Re-running it only fills in what is missing. The env name and languages are parameters (`-EnvName`, `-Langs`).

## OCR language codes

Pass one or more Tesseract codes joined by `+`: `-l eng`, `-l vie`, `-l eng+vie`.

Common: `eng`, `vie`, `deu`, `fra`, `spa`, `ita`, `por`, `rus`, `chi_sim`, `jpn`, `kor`. Full list: https://github.com/tesseract-ocr/tessdata_best

`tessdata_best` = highest accuracy (used here). `tessdata_fast` = faster, slightly lower accuracy.

## Quality / performance tips

- **DPI**: 300 is a good default. 400 helps small/stylised print; 200 is faster for large clean text.
- **Straight scans** work well out of the box. Rotated, skewed, or low-contrast scans benefit from deskew/binarisation (e.g. ImageMagick `-deskew`, or `ocrmypdf --deskew --clean`).
- OCR is ~1–3 s per page at 300 dpi; very large PDFs take minutes — run in the background.
- Prefer `-l` matching the document; mixing languages (`eng+vie`) is slower and can add noise.

## Troubleshooting

- **`tesseract not found`** → run `setup_env.ps1`, or set `TESSERACT` to the exe path.
- **`Error opening data file ... .traineddata`** → the language isn't installed. Add it: `setup_env.ps1 -Langs eng,vie`. The script sets `TESSDATA_PREFIX` to `~/.tessdata` automatically when the language lives there.
- **winget blocked / no admin** → install Tesseract manually (UB-Mannheim build) and re-run setup; it will detect `tesseract.exe`.
- **`conda` not on PATH** → call it by full path (`$env:USERPROFILE\miniconda3\Scripts\conda.exe`) or run `conda init`.
- **markitdown output looks like English gibberish on a foreign document** → that is a bad embedded OCR layer; ignore it and OCR with the correct `-l`.
- **Empty pages in OCR output** → the page image may be blank or extremely low resolution; check with `--dpi 400`.

## Related (optional)

If a downstream step needs a **PDF back out** of text/markdown, headless Chrome prints HTML to PDF well (handles Unicode/Vietnamese and A4 layout):

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu `
  --no-pdf-header-footer --print-to-pdf="out.pdf" "file:///C:/path/in.html"
```

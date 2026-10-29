# pdf-extract — reference

## Office files and legacy formats

markitdown handles OOXML (`.docx`, `.xlsx`, `.pptx`) and text PDFs natively.

Binary Office formats from before 2007 (`.doc`, `.xls`, `.ppt`) are **not** recognised — markitdown raises a conversion error rather than guessing. Convert first:

```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("C:\path\in.doc", $false, $true)
$doc.SaveAs2("C:\path\in.docx", 16)   # wdFormatDocumentDefault
$doc.Close(0)
$word.Quit()
```

- `SaveAs2` takes a plain string path here. The older `SaveAs([ref]$path, [ref]16)` form fails from PowerShell with *"Cannot convert the psobject value ... to type Object"*.
- Always `Close(0)` and `Quit()` in a `finally` block; a hidden Word instance with an unsaved document keeps the file locked and silently stalls the next run.
- LibreOffice equivalent: `soffice --headless --convert-to docx "C:\path\in.doc" --outdir "C:\path\out"`.

Long documents belong on disk, not in the chat:

```powershell
conda run -n pdf-ocr python -m markitdown "C:\path\in.docx" -o "C:\path\out.md"
```

## Why three tiers?

- **markitdown** reads documents that already contain a text layer. It is exact, instant, and needs no software install. It is the default for every file.
- **Tesseract** is the default OCR: fast (1–3 s/page), CPU-only, offline, tiny. Good for clean scans.
- **Unlimited-OCR** is a 3B vision-language model. It is 10–40× slower but preserves tables, headings and reading order as markdown, and reads any language without per-language data. Use it only when Tesseract is *wrong*, not merely imperfect.

Decision rule: **markitdown looks good → use it; empty/garbled → Tesseract; Tesseract garbles or returns nothing → Unlimited-OCR.**

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
2. **Tesseract-OCR** (`-Engine tesseract`, the default) — if `%ProgramFiles%\Tesseract-OCR\tesseract.exe` is missing, installs `UB-Mannheim.TesseractOCR` via winget.
3. **Language data** — default is `eng`, which ships with the installer (no download). Additional languages are downloaded (from `tessdata_best`) into `~/.tessdata` only when requested.
4. **Unlimited-OCR** (`-Engine uocr`) — installs llama.cpp (pinned Vulkan build) into `~/.pdf-extract/llama` and downloads the model + vision projector into `~/.pdf-extract/models` (~2.6 GB). **Only run this when the user has explicitly asked for this tier** — it is a large download and a slow engine. The model files are public, so no token is required; if `HF_TOKEN` is present in the environment it is used automatically (via a header file, so the token never appears on a command line and is never logged). Ask the user whether they want a token used before installing, but never echo it back.

Re-running only fills in what is missing. `-Engine both` sets up both OCR tiers.

## Layout

```
~/.pdf-extract/
  llama/llama-mtmd-cli.exe      llama.cpp b11963, Vulkan build
  models/Unlimited-OCR-Q4_K_M.gguf        1.86 GB
  models/mmproj-Unlimited-OCR-F16.gguf    774 MB
```

Override with `--model`, `--mmproj`, or the `UOCR_LLAMA` env var. No Vulkan-capable GPU? Re-run setup with `-LlamaZip <...-win-cpu-x64.zip>`; it still works, just slower.

## Tesseract language codes

Pass one or more codes joined by `+`: `-l eng`, `-l vie`, `-l eng+vie`.

Common: `eng`, `vie`, `deu`, `fra`, `spa`, `ita`, `por`, `rus`, `chi_sim`, `jpn`, `kor`. Full list: https://github.com/tesseract-ocr/tessdata_best

`tessdata_best` = highest accuracy (used here). `tessdata_fast` = faster, slightly lower accuracy.

## Measured behaviour

Synthetic A4 invoice page, 200 dpi render, known ground truth (4 invoice rows, 12 serial numbers, one Vietnamese paragraph):

| | Tesseract `eng+vie` | Unlimited-OCR Q4_K_M @200 | @300 |
|---|---|---|---|
| wall clock | 0.77 s | ~12 s | ~59 s |
| invoices | 4/4 | 4/4 | 4/4 |
| totals | 4/4 | 4/4 | 4/4 |
| Vietnamese markers | 3/4 | 3/4 | 3/4 |
| serial numbers | 12/12 | 12/12 | 12/12 |
| structure | flat text, "warehouse B checked" repeated 8× | `<table>` with header row and `colspan` | same |

Real 1969 newspaper scan (`tools/mtmd/test-1.jpeg` from llama.cpp):

| | Tesseract | Unlimited-OCR |
|---|---|---|
| result | **`Empty page!!`, 0 chars** | 4783 chars, correct masthead/date/volume |

That last row is the reason this tier exists. Tesseract's layout analysis gives up entirely on some real scans; the vision model reads them.

## Unlimited-OCR: required invocation

These flags are not optional. `scripts/ocr_pdf.py -e uocr` already supplies them:

```
--chat-template deepseek-ocr
--temp 0 --flash-attn off --no-warmup
-c 16384 -n 8192 -ngl 99
--dry-multiplier 0.8 --dry-base 1.75 --dry-allowed-length 35
--dry-penalty-last-n 128 --dry-sequence-breaker none
```

Why each matters:

- **`--chat-template deepseek-ocr`** — without it the process dies with `0xC0000409` (stack buffer overrun) immediately after template parsing. This looks like a corrupt model; it is not.
- **DRY sampler flags** — without them, dense pages fall into repetition loops (`batch NW24-0024-3`, `-2`, `-3`, …) and never emit `<|end|>`, wasting the whole token budget.
- **`--flash-attn off`** — the reference configuration for this architecture.

## Model choice, and the R-SWA caveat

`Unlimited-OCR` v1 is `DeepSeek-OCR` + R-SWA (reference sliding window attention: whole prompt is always visible, plus the last 128 generated tokens). Stock llama.cpp implements the decoder as **full MHA** and ignores the sliding window (llama.cpp PR #24969, merged). PR #24975, which implements true R-SWA, is still open.

Consequence: full attention is a *superset* of R-SWA, so outputs ≤128 tokens are mathematically identical. Beyond that the masks diverge. On the pages tested here it held up (no loop, all fields recovered), but **very long single-page outputs and multi-page one-shot parsing are unvalidated** on this path. The skill works page-by-page, which keeps each request inside the tested regime.

Use v1. v2 needs a hand-patched llama.cpp build, and converting v2 with the v1 converter produces fluent but wrong text (25% similarity on 3-page documents) because v2 changes both routing (DASH) and positional encoding.

## Quality / performance tips

- **DPI** is the main speed/quality dial for `-e uocr`. 200 is the default (~12 s/page); 300 recovers small print but costs ~60 s/page. Tesseract defaults to 300.
- **Straight scans** work well out of the box. Rotated, skewed, or low-contrast scans benefit from deskew/binarisation (e.g. ImageMagick `-deskew`, or `ocrmypdf --deskew --clean`).
- Run large PDFs in the background. Unlimited-OCR costs minutes per 10 pages.
- Prefer `-l` matching the document for Tesseract; mixing languages (`eng+vie`) is slower and can add noise. Unlimited-OCR needs no language selection.
- Output of `-e uocr` is markdown. If a downstream consumer wants flat text, strip the `<table>` tags or use `--prompt "Free OCR."`.

## Troubleshooting

- **`tesseract not found`** → run `setup_env.ps1`, or set `TESSERACT` to the exe path.
- **`Error opening data file ... .traineddata`** → the language isn't installed. Add it: `setup_env.ps1 -Langs eng,vie`. The script sets `TESSDATA_PREFIX` to `~/.tessdata` automatically when the language lives there.
- **Tesseract prints `Empty page!!` and writes 0 chars** → its layout analysis found no text. Re-run with `-e uocr`.
- **`llama-mtmd-cli not found`** → `pwsh -File scripts/setup_env.ps1 -Engine uocr`.
- **uocr exits with `0xC0000409` / `-1073740791`** → `--chat-template deepseek-ocr` was omitted or misspelled. The wrapper always passes it; only relevant if calling llama.cpp by hand.
- **uocr output repeats lines and never ends** → the DRY sampler flags were omitted, or `--max-tokens` is too low for the page.
- **uocr is very slow (>60 s/page on clean text)** → `--dpi` is at 300; drop to 200.
- **winget blocked / no admin** → install Tesseract manually (UB-Mannheim build) and re-run setup; it will detect `tesseract.exe`.
- **`conda` not on PATH** → call it by full path (`$env:USERPROFILE\miniconda3\Scripts\conda.exe`) or run `conda init`.
- **markitdown output looks like English gibberish on a foreign document** → that is a bad embedded OCR layer; ignore it and OCR again.
- **`FileConversionException` / `DocxConverter threw MissingDependencyException`** → the local `markitdown` install lacks the format extras. `pip install "markitdown[docx,pdf]"` and re-run. The MCP server is not affected.
- **markitdown refuses a `.doc`/`.xls`/`.ppt`** → legacy binary format, unsupported by design. Convert to `.docx`/`.xlsx`/`.pptx` (Word COM or LibreOffice) and extract that.
- **`conda run` dies with `UnicodeEncodeError: 'charmap'` / `0xC0000409`-style crash on a Unicode path** → conda relays the child's stdout through the console codepage (cp1252 on many Windows hosts). Either call the env interpreter directly (`C:\Users\<you>\miniconda3\envs\pdf-ocr\python.exe ...`) or set `$env:PYTHONIOENCODING = "utf-8"` first. The conversion itself already succeeded when this happens.
- **Vietnamese/CJK text prints as `?` or `�` in the terminal** → console rendering, not corruption. Check the saved file with Python before "fixing" anything: `python -c "import io;t=io.open(r'C:\p\out.md',encoding='utf-8').read();print(len(t), sum(1 for c in t if ord(c)>127))"`. A large non-ASCII count means the text is intact.
- **Empty pages in OCR output** → the page image may be blank or extremely low resolution; check with `--dpi 400`.

## Related (optional)

If a downstream step needs a **PDF back out** of text/markdown, headless Chrome prints HTML to PDF well (handles Unicode/Vietnamese and A4 layout):

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu `
  --no-pdf-header-footer --print-to-pdf="out.pdf" "file:///C:/path/in.html"
```

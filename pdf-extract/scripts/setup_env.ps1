<#
  Idempotent setup for the pdf-extract skill.

  Ensures, depending on -Engine:
    tesseract : conda env "pdf-ocr" (Python 3.12 + PyMuPDF)
                Tesseract-OCR installed (via winget if missing)
                requested Tesseract language data in ~/.tessdata
    uocr      : same conda env
                llama.cpp release (Vulkan build) in ~/.pdf-extract/llama
                Unlimited-OCR v1 GGUF + mmproj in ~/.pdf-extract/models

  Safe to re-run; only fills in what is missing.

  The uocr tier is a ~3.5 GB download. Run it only when the user explicitly
  asked for that tier. The model files are public: no token is required, but
  if HF_TOKEN is set in the environment it is used (via a header file, so it
  never lands on a command line). Ask the user about a token before installing.

  Usage:
    pwsh -File setup_env.ps1                   # Tesseract only (default)
    pwsh -File setup_env.ps1 -Langs eng,vie    # add Tesseract languages
    pwsh -File setup_env.ps1 -Engine uocr      # add the Unlimited-OCR tier (~3.5 GB)
    pwsh -File setup_env.ps1 -Engine both -Langs eng,vie
    pwsh -File setup_env.ps1 -Engine uocr -LlamaZip <url>   # e.g. a -cpu-x64 build
#>
param(
  [ValidateSet("tesseract", "uocr", "both")]
  [string]$Engine  = "tesseract",
  [string]$EnvName = "pdf-ocr",
  [string]$Langs   = "eng",
  [string]$LlamaZip = "https://github.com/ggml-org/llama.cpp/releases/download/b11963/llama-b11963-bin-win-vulkan-x64.zip"
)

$ErrorActionPreference = "Stop"
$vendor   = Join-Path ${env:ProgramFiles} "Tesseract-OCR"
$tessExe  = Join-Path $vendor "tesseract.exe"
$tessdata = Join-Path $env:USERPROFILE ".tessdata"

$ocrHome  = Join-Path $env:USERPROFILE ".pdf-extract"
$llamaDir = Join-Path $ocrHome "llama"
$modelDir = Join-Path $ocrHome "models"
$llamaExe = Join-Path $llamaDir "llama-mtmd-cli.exe"

$needTess  = $Engine -in @("tesseract", "both")
$needUocr  = $Engine -in @("uocr", "both")

function Get-HfFile($url, $dest, $expectedBytes, $label) {
  if ((Test-Path $dest) -and ((Get-Item $dest).Length -eq $expectedBytes)) {
    Write-Host "[ok] $label present."
    return
  }
  Write-Host "[..] downloading $label ..."
  $hdr = $null
  if ($env:HF_TOKEN) {
    # header file keeps the token out of the process command line
    $hdr = Join-Path $env:TEMP "pdf-extract-hf.hdr"
    Set-Content -Path $hdr -Value ("Authorization: Bearer " + $env:HF_TOKEN) -NoNewline -Encoding ascii
  }
  try {
    $args = @("-L", "--retry", "5", "--retry-all-errors", "-sS", "-C", "-", "-o", $dest, $url)
    if ($hdr) { $args = @("-H", "@$hdr") + $args }
    & curl.exe @args
    if ($LASTEXITCODE -ne 0) { throw "curl failed with exit $LASTEXITCODE" }
  } finally {
    if ($hdr -and (Test-Path $hdr)) { Remove-Item $hdr -Force }
  }
  $got = (Get-Item $dest).Length
  if ($got -ne $expectedBytes) {
    throw "$label size mismatch: got $got, expected $expectedBytes. Delete it and re-run."
  }
  Write-Host "[ok] $label downloaded."
}

# --- 1. conda env ---------------------------------------------------------
$hasEnv = $false
try {
  $list = (& conda env list) 2>$null | Out-String
  if ($list -match "(?m)^\s*$([regex]::Escape($EnvName))\s") { $hasEnv = $true }
} catch { $hasEnv = $false }

if ($hasEnv) {
  Write-Host "[ok] conda env '$EnvName' already exists."
} else {
  Write-Host "[..] creating conda env '$EnvName' ..."
  & conda create -n $EnvName python=3.12 -y
}
Write-Host "[..] ensuring PyMuPDF in '$EnvName' ..."
& conda run -n $EnvName python -m pip install --quiet --upgrade pymupdf

# --- 2. Tesseract ---------------------------------------------------------
if ($needTess) {
  if (Test-Path $tessExe) {
    Write-Host "[ok] Tesseract present: $tessExe"
  } else {
    Write-Host "[..] installing Tesseract-OCR via winget ..."
    & winget install --id UB-Mannheim.TesseractOCR --exact --silent `
        --accept-source-agreements --accept-package-agreements
    if (-not (Test-Path $tessExe)) {
      throw "Tesseract not found at $tessExe after install. Install it manually and re-run."
    }
    Write-Host "[ok] Tesseract installed: $tessExe"
  }

  New-Item -ItemType Directory -Force -Path $tessdata | Out-Null
  foreach ($lang in ($Langs -split '[,;\s]+')) {
    $l = $lang.Trim()
    if (-not $l) { continue }
    $dest    = Join-Path $tessdata "$l.traineddata"
    $builtin = Join-Path $vendor "tessdata\$l.traineddata"
    if (Test-Path $dest) {
      Write-Host "[ok] $l.traineddata present."
    } elseif (Test-Path $builtin) {
      Copy-Item $builtin $dest -Force
      Write-Host "[ok] copied bundled $l.traineddata."
    } else {
      Write-Host "[..] downloading $l.traineddata ..."
      Invoke-WebRequest -UseBasicParsing `
        -Uri "https://github.com/tesseract-ocr/tessdata_best/raw/main/$l.traineddata" `
        -OutFile $dest
      Write-Host "[ok] $l.traineddata downloaded."
    }
  }
}

# --- 3. Unlimited-OCR (llama.cpp + GGUF) ----------------------------------
if ($needUocr) {
  New-Item -ItemType Directory -Force -Path $llamaDir, $modelDir | Out-Null

  if (Test-Path $llamaExe) {
    Write-Host "[ok] llama.cpp present: $llamaDir"
  } else {
    $zip = Join-Path $ocrHome "llama.zip"
    Write-Host "[..] downloading llama.cpp ..."
    & curl.exe -L --retry 5 --retry-all-errors -sS -o $zip $LlamaZip
    if ($LASTEXITCODE -ne 0) { throw "failed to download llama.cpp ($LlamaZip)" }
    Expand-Archive -Path $zip -DestinationPath $llamaDir -Force
    Remove-Item $zip -Force
    if (-not (Test-Path $llamaExe)) {
      throw "llama-mtmd-cli.exe not found after unzip; check -LlamaZip"
    }
    Write-Host "[ok] llama.cpp installed: $llamaDir"
  }

  $hf = "https://huggingface.co/sahilchachra/Unlimited-OCR-GGUF/resolve/main"
  Get-HfFile "$hf/Unlimited-OCR-Q4_K_M.gguf" (Join-Path $modelDir "Unlimited-OCR-Q4_K_M.gguf") 1950326784 "Unlimited-OCR-Q4_K_M.gguf (~1.8 GB)"
  Get-HfFile "$hf/mmproj-Unlimited-OCR-F16.gguf" (Join-Path $modelDir "mmproj-Unlimited-OCR-F16.gguf") 811876448 "mmproj-Unlimited-OCR-F16.gguf (~774 MB)"
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "  env      : $EnvName"
if ($needTess) {
  Write-Host "  tesseract: $tessExe"
  Write-Host "  tessdata : $tessdata"
}
if ($needUocr) {
  Write-Host "  llama    : $llamaDir"
  Write-Host "  models   : $modelDir"
}

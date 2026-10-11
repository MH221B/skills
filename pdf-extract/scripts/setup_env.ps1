<#
  Idempotent setup for the pdf-extract skill.

  Ensures:
    - conda env "pdf-ocr" (Python 3.12 + PyMuPDF) exists
    - Tesseract-OCR is installed (via winget if missing)
    - requested Tesseract language data is available in ~/.tessdata

  Safe to re-run; only fills in what is missing.

  Usage:
    pwsh -File setup_env.ps1                 # default: English only (bundled, no download)
    pwsh -File setup_env.ps1 -Langs eng,vie  # add languages a document actually needs
    pwsh -File setup_env.ps1 -EnvName pdf-ocr -Langs deu
#>
param(
  [string]$EnvName = "pdf-ocr",
  [string]$Langs   = "eng"
)

$ErrorActionPreference = "Stop"
$vendor = Join-Path ${env:ProgramFiles} "Tesseract-OCR"
$tessExe = Join-Path $vendor "tesseract.exe"
$tessdata = Join-Path $env:USERPROFILE ".tessdata"

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

# --- 3. language data -----------------------------------------------------
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

Write-Host ""
Write-Host "Setup complete."
Write-Host "  env      : $EnvName"
Write-Host "  tesseract: $tessExe"
Write-Host "  tessdata : $tessdata"

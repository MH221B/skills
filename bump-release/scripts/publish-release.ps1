[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Version,
    [Parameter(Mandatory = $true)][string]$NotesFile,
    [string]$Repo = ''
)

$ErrorActionPreference = 'Stop'

if ($Version -notmatch '^v\d+\.\d+\.\d+$') { throw "Version '$Version' must look like v0.3.4 (tags in this repo use v0.x.y)." }
if (-not (Test-Path -LiteralPath $NotesFile -PathType Leaf)) { throw "Release notes file was not found at '$NotesFile'." }

function Invoke-Checked {
    param([string]$Label, [scriptblock]$Action)
    & $Action
    if ($LASTEXITCODE -ne 0) { throw "$Label failed (exit code $LASTEXITCODE)." }
}

Write-Output "Tagging $Version..."
Invoke-Checked "git tag $Version" { git tag $Version }
Invoke-Checked "git push origin $Version" { git push origin $Version }

Write-Output "Creating release $Version..."
if ($Repo) {
    Invoke-Checked "gh release create $Version" { gh release create $Version --repo $Repo --title $Version --notes-file $NotesFile }
} else {
    Invoke-Checked "gh release create $Version" { gh release create $Version --title $Version --notes-file $NotesFile }
}

$view = if ($Repo) {
    gh release view $Version --repo $Repo --json tagName,isDraft,isPrerelease --jq '{tagName,isDraft,isPrerelease}'
} else {
    gh release view $Version --json tagName,isDraft,isPrerelease --jq '{tagName,isDraft,isPrerelease}'
}
Write-Output $view

$parsed = ($view | ConvertFrom-Json)
if ($parsed.isDraft) { throw "Release $Version is a draft; it must be published. Edit the release to publish it." }
if ($parsed.isPrerelease) { throw "Release $Version is a prerelease; the bootstrap rejects prereleases. Edit the release to remove the prerelease flag." }

Write-Output "Published $Version."

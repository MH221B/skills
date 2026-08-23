---
name: bump-release
description: >
  Cut a new version and publish it as a GitHub release with clean,
  correctly-formatted release notes. Determines the right semver bump from the
  changes, ensures the work is committed and pushed, tags, and publishes via
  `gh` using a notes file to avoid shell-escaping bugs. Verifies the release is
  not a draft or prerelease and is marked Latest. Use when the user wants to
  bump or tag a release, cut a new version, or fix release notes. Trigger words
  bump, release, tag, publish, cut a release, new version.
---

# Bump & Release

Publish a new tagged GitHub release with well-formed release notes. Two rules prevent the mistakes that plague ad-hoc releases:

1. **Write the notes to a temp `.md` file** and pass it with `--notes-file`. Never pass notes inline to `gh` — backticks, `$`, and parentheses get mangled by the shell.
2. **One bullet per line, no internal wrapping.** Each `- ` item starts on its own line or it won't render as a list; GitHub soft-wraps long text for you.

Verify the published release before declaring success.

## 0. Confirm the version

- Ask the user which version to cut, or propose one from `git log`:
  - `fix:` / bug fixes → next patch (`v0.3.3` → `v0.3.4`)
  - `feat:` / new capability → next minor (`v1.2.0` → `v1.3.0`)
  - breaking change → next major
- Match the repo's existing tag style: `git tag --sort=-v:refname`. This repo uses `v0.x.y` (e.g. `v0.3.4`).

## 1. Land the changes first

The release archive is built from the tag, so what you tag is exactly what ships. Commit and push everything intended before tagging:

```powershell
git add -A
git commit -m "<conventional message>"
git push origin main
```

## 2. Write the notes to a temp file

Build a `.md` file in the temp dir with a single-quoted here-string (so nothing is interpreted):

```powershell
$notes = Join-Path $env:TEMP ("release-notes-" + [guid]::NewGuid().ToString('N') + ".md")
@'
- First bullet, one line.
- Second bullet, one line.
'@ | Set-Content -LiteralPath $notes -Encoding UTF8
```

### Notes formatting rules
- Each `- ` bullet starts on a **new line**.
- Keep each bullet on a **single line** — no hard wrapping inside it.
- Separate a list from the following paragraph with a **blank line**.
- Backticks are literal in the file; do not escape them.
- Do not use `--notes "..."` inline; use `--notes-file`.

## 3. Tag and publish

```powershell
git tag v0.3.4
git push origin v0.3.4
gh release create v0.3.4 --title v0.3.4 --notes-file $notes
```

Or use the helper (handles tag, push, release, and checks):

```powershell
powershell -File scripts/publish-release.ps1 -Version v0.3.4 -NotesFile $notes
```

## 4. Verify

```powershell
gh release view v0.3.4 --json tagName,isDraft,isPrerelease --jq '{tagName,isDraft,isPrerelease}'
gh release list --limit 1
```

Confirm `isDraft: false`, `isPrerelease: false`, and the release is marked **Latest**. If the user cares about the exact wording, keep notes concise and factual.

## Checklist

- [ ] Version confirmed with user / justified from commits
- [ ] Changes committed & pushed to `main`
- [ ] Notes written to a temp file, not inline
- [ ] Each bullet on its own line, no internal wrapping
- [ ] Tag created, pushed, release created with `--notes-file`
- [ ] Verified not draft/prerelease and marked Latest
- [ ] Reported the release URL to the user

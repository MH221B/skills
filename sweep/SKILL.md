---
name: sweep
description: Clean skill artifacts out of the OS temp dirs after multiple sessions: handoff docs, prototype builds, debug HTML reports, captured traces, harness scripts. Lists what it found, flags items older than a day as deletable, and removes only what you confirm. Use when temp dirs accumulate junk, or with "sweep", "clean temp", "clear out /tmp". Other temp files are never touched.
argument-hint: "[dry-run | all]"
disable-model-invocation: true
---

# Sweep

Remove what skill sessions left behind in the OS temp dirs. Only recognizable skill artifacts get touched. Everything else in the temp dir stays.

## 1. Scan

Check `$TMPDIR`, falling back to `/tmp` (Linux/macOS), and `/var/tmp`. Match artifacts by pattern and source:

- `handoff-*.md` from the `handoff` skill. These usually outlive their use once `pickup` has read them.
- Throwaway prototype builds and demo folders from `prototype`.
- Architecture review reports, `*.html`, from `improve-codebase-architecture`.
- Captured traces and log dumps from `diagnosing-bugs`: `*.har`, `*.log`, `*.dump`, and repro harness scripts or folders.
- Anything else whose name or content matches a known skill's output.

Do not follow symlinks that point outside the temp dirs.

## 2. Report

For each hit, show the path, size, age, and which skill likely made it. Then split the list:

- Deletable: older than 1 day. A handoff saved today still needs to survive for `pickup`.
- Protected: newer. Stays.

## 3. Confirm

Show the deletable list and ask which to remove. Delete only what you confirm.

- `all` proposes deleting every deletable item, still with one confirmation before anything is removed.
- `dry-run` prints the full report and deletes nothing.

## 4. Delete

Remove the confirmed items. State what went and how much space it freed.

## Boundaries

- Never delete anything that isn't a recognizable skill artifact. Other processes share the temp dirs.
- Never touch symlinks pointing outside the temp dirs.
- Nothing is deleted without your confirmation.
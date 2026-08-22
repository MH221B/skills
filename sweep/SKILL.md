---
name: sweep
description: Clean agent-session artifacts out of the OS temp dirs after multiple sessions: handoff docs, throwaway scripts and harnesses, prototype builds, debug HTML reports, captured traces, log dumps. Lists what it found, flags items older than a day as deletable, and removes only what you confirm. Use when temp dirs accumulate junk, or with "sweep", "clean temp", "clear out /tmp". Other temp files are never touched.
argument-hint: "[dry-run | all]"
disable-model-invocation: true
---

# Sweep

Remove what agent sessions left behind in the OS temp dirs. Only session artifacts get touched. Everything else in the temp dir stays.

## 1. Scan

Check `$TMPDIR`, falling back to `/tmp` (Linux/macOS), and `/var/tmp`. Also check the agent's own session-temp root if one exists, commonly `/tmp/opencode`; everything under that root counts as session-owned.

Treat these as session artifacts:

- Everything under a session-temp root such as `/tmp/opencode`.
- Handoff docs: `handoff-*.md`.
- Scripts and harnesses: throwaway `.sh` files, `hitl-loop*.sh` repro loops, `repro*` and `bench*` scripts, fixture inputs used to diff against known-good output.
- Builds and outputs: `prototype` folders, architecture reports (`.html`), captured traces (`*.har`), log dumps (`*.log`, `*.dump`).
- Debug logs tagged `[DEBUG-...]` left by `diagnosing-bugs`.
- Anything else that names or looks like an agent run, down to a lone stub file or empty directory a skill left behind.

Do not follow symlinks that point outside the temp dirs.

## 2. Report

For each hit, show the path, size, age, and why it counts as a session artifact. Then split the list:

- Deletable: older than 1 day. A handoff saved today still needs to survive for `pickup`.
- Protected: newer. Stays.

## 3. Confirm

Show the deletable list and ask which to remove. Delete only what you confirm.

- `all` proposes deleting every deletable item, still with one confirmation before anything is removed.
- `dry-run` prints the full report and deletes nothing.

## 4. Delete

Remove the confirmed items. State what went and how much space it freed.

## Boundaries

- Never delete anything that isn't a session artifact. Other processes share the temp dirs.
- Never touch symlinks pointing outside the temp dirs.
- Nothing is deleted without your confirmation.
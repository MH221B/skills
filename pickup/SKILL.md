---
name: pickup
description: Resume work in a new session from a handoff document. Finds the newest handoff doc, or the path you give. Reads the referenced specs, plans, ADRs, and git state, then presents a resume brief and waits for a go-ahead. Use when starting a session with "pick up where we left off", "continue the work", or after a handoff doc or path has been passed to you.
argument-hint: "[path to handoff doc; defaults to the newest found]"
disable-model-invocation: true
---

# Pickup

Start a new session where `handoff` ended it. Orient fully before touching anything, then wait for the go-ahead.

## 1. Locate the handoff doc

- Use a path passed as an argument if there is one.
- Otherwise scan the handoff locations for the newest `handoff-*.md`:
  - `$TMPDIR`, falling back to `/tmp` (Linux/macOS). Also check `/var/tmp` if nothing is found.
  - Filenames use `handoff-YYYY-MM-DD_HHMM_<topic>.md` (see `handoff`), so "newest" is the lexicographically largest filename. If dates are ambiguous, compare file mtimes.
- If no doc is found, say so and ask the user for the path.

## 2. Read it fully

Read the whole document before touching any state.

## 3. Restore context

Pull in everything the doc references:

- Read each file it cites: specs, plans, ADRs, docs. Skip any path that no longer exists.
- Check live git state: `git branch --show-current`, `git log --oneline -5`, `git status --short`, `git stash list`.
- Verify claims about done work actually hold: a commit exists, a file changed as described. Flag anything that doesn't.

## 4. Resume brief

Present, compactly:

- Where we are: branch, recent commits, uncommitted or unstaged work.
- What's done: from the doc, verified against the repo.
- What's next: the doc's next steps, in order.
- Skills to use: the doc's "suggested skills" list. Load them via the Skill tool when needed.
- Discrepancies: anything that doesn't match the doc (branch changed, work already landed, files gone).

## 5. Confirm before continuing

Do **not** continue the work yet. State the next concrete step and ask the user to confirm before you act.

## Boundaries

- Content already captured in handed-off artifacts (specs, plans, commits, diffs) is referenced, not re-stated.
- The doc should arrive redacted. If you spot a secret while reading, stop and flag it instead of repeating it.
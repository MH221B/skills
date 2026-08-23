---
name: setup-domain-docs
description: Sets up the domain-docs convention (CONTEXT.md / docs/adr/ layout and consumer rules) so skills like improve-codebase-architecture, diagnosing-bugs, and tdd know how to read the repo's domain language and architectural decisions. Writes an `## Agent skills` block in AGENTS.md/CLAUDE.md and `docs/agents/domain.md`. Run before first use of those skills, or if they appear to be missing context about domain docs.
disable-model-invocation: true
---

# Setup Domain Docs

Scaffold the per-repo domain-docs configuration that the engineering skills assume. The skills `improve-codebase-architecture`, `diagnosing-bugs`, and `tdd` read `CONTEXT.md` for the project's domain language and `docs/adr/` for past architectural decisions.

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with the user, then write.

## Process

### 1. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `CONTEXT.md` and `CONTEXT-MAP.md` at the repo root
- `docs/adr/` and any `src/*/docs/adr/` directories (multi-context repos)
- `AGENTS.md` and `CLAUDE.md` at the repo root: does either exist? Is there already an `## Agent skills` section in either?
- `docs/agents/`: does this skill's prior output already exist?

### 2. Present findings and ask

Summarise what's present and what's missing. Then confirm the domain-docs layout.

> Explainer: Some skills (`improve-codebase-architecture`, `diagnosing-bugs`, `tdd`) read a `CONTEXT.md` file to learn the project's domain language, and `docs/adr/` for past architectural decisions. They need to know whether the repo has one global context or multiple (e.g. a monorepo with separate frontend/backend contexts) so they look in the right place.

Confirm the layout:

- **Single-context**: one `CONTEXT.md` + `docs/adr/` at the repo root. Most repos are this.
- **Multi-context**: `CONTEXT-MAP.md` at the root pointing to per-context `CONTEXT.md` files (typically a monorepo).

### 3. Confirm and edit

Show the user a draft of:

- The `## Agent skills` block to add to whichever of `CLAUDE.md` / `AGENTS.md` is being edited (see step 4 for selection rules)
- The contents of `docs/agents/domain.md`

Let them edit before writing.

### 4. Write

**Pick the file to edit:**

- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask the user which one to create: don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa): always edit the one that's already there.

If an `## Agent skills` block already exists in the chosen file, update its contents in-place rather than appending a duplicate. Don't overwrite user edits to the surrounding sections.

The block:

```markdown
## Agent skills

### Domain docs

[one-line summary of layout: "single-context" or "multi-context"]. See `docs/agents/domain.md`.
```

Then write `docs/agents/domain.md` using the [domain.md](./domain.md) seed template in this skill folder as a starting point.

### 5. Done

Tell the user the setup is complete and which engineering skills will now read from `docs/agents/domain.md`. Mention they can edit `docs/agents/domain.md` directly later: re-running this skill is only necessary if the repo moves between single- and multi-context layouts.
# learning-records/<NNNN>-<slug>.md Format

Learning records are the ADR (Architecture Decision Record) of teaching: short, decision-grade notes that capture *what was actually learned* and *why it matters*. They are sparse by design.

## Rules

1. **Sequential numbering.** `<NNNN>` is a zero-padded 4-digit sequence number (`0001`, `0002`, …). One sequence per workspace.
2. **Dash-case slug.** Filename is `<NNNN>-<slug>.md` where `<slug>` is dash-case and short.
3. **Created only when real learning happens.** Specifically: demonstrated genuine understanding, disclosed prior knowledge, corrected a misconception, or shifted the mission. Coverage alone is not learning.
4. **Does NOT qualify:** mere coverage, glossary definitions, session-by-session journals.
5. **1–3 sentence body.** Keep it short. A title and a few sentences are usually enough.
6. **Supersede, don't delete.** When a learning record is later corrected, replaced, or expanded, create a new record and mark the old one's `Status` as `superseded by LR-NNNN`. The old file stays.

## Frontmatter

```yaml
---
title: <short, specific title>
status: active | superseded by LR-NNNN
date: <YYYY-MM-DD>
evidence: <optional — what demonstrates this learning, e.g. "user explained X correctly in their own words">
implications: <optional — what this means for future teaching>
related: <optional — list of related learning record numbers, e.g. [0001, 0003]>
---
```

## Template

```markdown
---
title: <title>
status: active
date: <YYYY-MM-DD>
---

<1–3 sentence body capturing the learning. Specific, not generic.>
```

## Anti-patterns

- Creating a learning record for every session.
- Vague titles ("Learned about X").
- Long bodies (more than 3 sentences usually means it's not a learning record, it's a journal entry).
- Deleting old records instead of superseding.

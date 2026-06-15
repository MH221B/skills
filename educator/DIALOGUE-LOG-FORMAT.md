# dialogue-logs/<topic-slug>.md Format

A dialogue log is the append-only record of all Socratic sessions on a single topic. One file per topic. New sessions are appended; nothing is rewritten.

## File naming

`<topic-slug>.md` where `<topic-slug>` is lowercase, dash-separated, descriptive. Examples: `async-javascript.md`, `calculus-derivatives.md`, `world-war-2.md`.

## File structure

```markdown
# Dialogue Log: <Topic Title>

**Topic slug:** <topic-slug>
**Mission ref:** <link or quote from MISSION.md>
**First session:** <YYYY-MM-DD>
**Last updated:** <YYYY-MM-DD>
**Sessions:** <count>

## Baseline Assessment

<filled in at first session, updated only if shift-prone dimensions change>

- Conceptual understanding: <level>
- Problem-solving approach: <notes>
- Tool fluency: <notes, if coding>
- Confidence: <1–5>
- Learning context: <notes>

## Learning Goals

- <goal 1>
- <goal 2>

## Successful Mental Models

### MM-001: <short name>
- **Captured:** <YYYY-MM-DD>
- **Why it worked:** <what made this mental model click for the user>

## Identified Misconceptions & Fixes

### MIS-001: <short description of misconception>
- **Captured:** <YYYY-MM-DD>
- **Why it was wrong:** <the flawed assumption>
- **Fix:** <what corrected it>

## Progress Over Time

### Session 1 — <YYYY-MM-DD>
- **Phase 1 (Assessment):** <summary>
- **Phase 2 (Blueprinting):** <summary>
- **Phase 3 (Progressive Execution):** <summary>
- **Phase 4 (Socratic Debugging):** <summary>
- **Phase 5 (Metacognitive Closure):** <summary>
- **New mental models:** [MM-002]
- **New misconceptions:** []
- **New glossary terms:** [event-loop]

### Session 2 — <YYYY-MM-DD>
- ...

## Quiz Performance Tracking

<quiz logs in the unified format>

## Related Topics & Cross-Links

- **Depends on:** [topic-slug-1, topic-slug-2]
- **Prerequisite for:** [topic-slug-3]
- **Reinforced by:** [topic-slug-4]
```

## Quiz log format (unified with lesson mode)

Append under `## Quiz Performance Tracking` using this exact shape:

```markdown
### Quiz: <YYYY-MM-DD> <topic-slug>
- mode: dialogue
- difficulty: foundational | applied | advanced
- question: <short label>
- correct: yes | no | partial
- notes: <one-line observation>
```

## Rules

1. **Append-only.** Never rewrite, reorder, or delete prior sessions.
2. **One file per topic.** If the user pivots to a new topic, create a new file.
3. **Update `Last updated` and `Sessions` count** at the top after each new session.
4. **Update `## Related Topics & Cross-Links`** when new dependencies or reinforcements emerge.

## Anti-patterns

- Rewriting old sessions "to clean them up."
- Merging sessions across topics into one log.
- Skipping the `## Progress Over Time` section.
- Putting mental models and misconceptions in the session entries themselves (they live in their own top-level sections).

# RESOURCES.md Format

`RESOURCES.md` holds the curated, high-trust sources the agent uses for lesson mode. In dialogue mode, the agent may consult these for verification when the user challenges an answer.

## Rules

1. **High-trust only.** Primary sources, recognized experts, peer-reviewed material, moderated communities of practice. No random blog posts, no SEO content farms.
2. **Annotate every entry.** Each source gets a one-line note: what it covers + when to reach for it.
3. **Group by Knowledge vs Wisdom.** Knowledge = facts, concepts, primary material. Wisdom = practitioner experience, design tradeoffs, common pitfalls.
4. **Mark gaps explicitly.** If no good resource exists for an area the mission needs, add a `## Gaps` section entry. The agent will pause to research or ask the user for a source rather than invent one.
5. **Prune ruthlessly.** If a resource hasn't been used or referenced in months, remove it.
6. **Record community opt-outs.** If a user has explicitly asked not to use a particular community or author, record it under a `## Opt-outs` section so future sessions respect it.

## Template

```markdown
# Resources

## Knowledge

### <topic-area>

- **<title>** — <author or publisher>. <URL>. <one-line: what it covers> + <when to reach for it>.
- **<title>** — ...

## Wisdom

### <topic-area>

- **<title>** — <author or publisher>. <URL>. <one-line: what it covers> + <when to reach for it>.

## Gaps

- <topic-area>: <what's missing, why, and what would close the gap>

## Opt-outs

- <community, author, or domain> — <reason the user opted out>
```

## Anti-patterns

- A "Resources" section that's actually a bookmark dump with no annotations.
- Resources without URLs (or with broken ones).
- Treating blog posts and primary sources as equivalent in trust.
- Letting `## Gaps` grow without ever closing entries.

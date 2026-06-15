# GLOSSARY.md Format

The glossary is the canonical terminology for the workspace, shared by both modes. Both modes consult it before introducing a new term; both modes update it only after the user demonstrates understanding.

## Rules

1. **Add a term only when the user understands it**, not when it's first introduced. "Understands" means: can use it correctly in their own words.
2. **Be opinionated.** Pick the best term. List alternatives as `_Avoid_: ...` so future sessions use the canonical form.
3. **Tight definitions.** One or two sentences. The definition should say what the term **is**, not just what it's used for.
4. **Use the glossary's own terms.** Definitions compose — a definition of "closure" can refer to "scope" if both are in the glossary.
5. **Group with subheadings** when clusters emerge (e.g. `## Asynchrony`, `## Memory`).
6. **Flag ambiguities.** If a term has multiple conflicting meanings in the literature, note it explicitly.
7. **Revise in place** as understanding deepens. Bump a learning record if the revision is significant.

## Template

```markdown
# Glossary

## <cluster-1>

### <term>

- **Definition:** <one or two sentences>
- _Avoid:_ <synonym or alternative name to avoid>

### <term>
- **Definition:** ...

## <cluster-2>
...
```

## Anti-patterns

- Adding terms the moment they're mentioned.
- Definitions that just restate the term ("A closure is when something is closed").
- Synonyms listed as separate "terms" (pick one, list the rest as `_Avoid_`).
- Letting the glossary grow past what's actually understood.

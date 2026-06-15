# MISSION.md Format

A `MISSION.md` file declares the user's reason for learning. One mission per workspace. Unrelated topics → new workspace.

## Rules

1. **One mission per workspace.** If the user wants to learn a new, unrelated topic, start a new workspace.
2. **Concrete over abstract.** "Run a half marathon by October" beats "get fitter." "Ship a CLI tool that scrapes Hacker News by next month" beats "learn Rust."
3. **Push back on vagueness.** If the mission is too abstract, the agent must interview the user before producing any lesson or starting any dialogue.
4. **Revise when reality shifts.** When the mission changes (normal during learning), update `MISSION.md` *and* add a learning record capturing the shift. Confirm with the user first.
5. **Keep it short.** If `MISSION.md` runs past a screen, it has stopped being a compass and started being a plan.

## Template

```markdown
# Mission

**Why I'm learning:** <one sentence — the concrete goal>

**Success looks like:** <observable outcome, dated if possible>

**Constraints:** <time, prior knowledge, tools, budget — anything that shapes what to teach>

**Out of scope:** <topics the agent should not waste time on>
```

## Anti-patterns

- Vague missions ("learn X", "understand Y better") — push back.
- Missions that try to cover unrelated topics — split into separate workspaces.
- Missions without an observable success criterion.
- Missions that grow past a screen — split or trim.

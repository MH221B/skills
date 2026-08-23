# Workflow Skills

Skills for working with a coding assistant: planning, building, debugging, and reviewing without the usual ceremony.

Most come from Matt Pocock's skill set, some from obra's Superpowers. The collection is trimmed for a solo workflow: TDD is opt-in rather than the default, and the issue-tracker pipeline (to-issues, to-prd, triage) is gone. The skills follow the Agent Skills format, so any host that loads skills can run them: opencode, Claude Code, Codex, and others.

## Skills

Each skill lives in its own folder with a `SKILL.md` file. Here the folder is registered as opencode's global skill source, but the layout is the standard Agent Skills one, so the same folders work anywhere. An individual skill loads when its description matches what you're doing, and you can also invoke one by name.

### Planning and design
- **brainstorming**: Explore requirements and design before implementing
- **writing-plans**: Write step-by-step implementation plans for multi-step tasks
- **grilling**: Grill the user relentlessly about a plan, decision, or idea
- **grill-me**: Stress-test ideas through intensive questioning
- **grill-with-docs**: Grill against existing domain knowledge, creating ADRs and a glossary as you go
- **implement**: Implement a piece of work from a spec or tickets (uses `/tdd` where pre-agreed, then `/code-review`)

### Development and debugging
- **tdd**: Red-green-refactor test-driven development. Only invoked when asked for
- **diagnosing-bugs**: Feedback-loop diagnosis for hard bugs and performance regressions
- **prototype**: Build throwaway prototypes to explore designs
- **resolving-merge-conflicts**: Resolve an in-progress git merge or rebase conflict

### Research
- **research**: Investigate a question against high-trust primary sources and capture findings as a Markdown file

### Code and architecture
- **codebase-design**: Shared vocabulary for designing deep modules
- **improve-codebase-architecture**: Find refactoring opportunities and deepening paths
- **domain-modeling**: Build and sharpen the project's domain model (CONTEXT.md and ADRs)
- **code-review**: Review changes since a fixed point along Standards and design axes
- **write-a-skill**: Create new agent skills with proper structure

### Minimalism and code review
- **ponytail**: Make the agent write the smallest thing that works. It questions whether code needs to exist, reaches for the standard library before a custom abstraction, and cuts needless structure. Levels: lite, full (default), ultra
- **ponytail-review**: Review a diff for over-engineering and list what to delete
- **ponytail-audit**: The same review across the whole repo instead of a diff
- **ponytail-debt**: Gather `ponytail:` shortcuts you deferred into one ledger so they get tracked, not forgotten

### Handoff and sessions
- **handoff**: Compact the current conversation into a handoff document for another agent
- **pickup**: Resume work in a new session from the newest handoff document
- **sweep**: Clean agent-session artifacts out of the OS temp dirs

### Utilities
- **find-skills**: Discover and install available skills
- **caveman**: Ultra-compressed communication mode (roughly 75% fewer tokens)
- **wait-what**: Stop and re-pitch when the last message didn't land
- **setup-domain-docs**: Set up the domain-docs convention (CONTEXT.md / ADRs) for the engineering skills
- **unslop**: Strip AI tells from writing and put a human voice back in

## Workflow

One unit of work, top to bottom:

1. **grill** the idea with the user. Interview until the design tree is settled and every branch is visited. Use `grill-with-docs` when decisions should also land in `CONTEXT.md` and the ADRs.
2. **brainstorm** the settled idea into a written spec. Subagents gather project context in parallel while you ask questions, propose approaches, present the design, and save the spec.
3. **ponytail-review** the spec. Cut features nobody asked for before they cost anything.
4. **prototype** the risky part of the design: a state model to push around or a few UI variants to look at. Cheap and throwaway, just to feel it before committing. Fold the verdict back into the spec.
5. **writing-plans** turns the spec into an implementation plan: files, code, verification, commits.
6. **implement** works the plan. It reads the spec, plan, and any prototype that exists, uses `/tdd` where pre-agreed, then runs `/code-review` when done.

In between and around it: `ponytail-review` again on the implementation diff, `diagnosing-bugs` when something breaks, and `handoff` to `pickup` to `sweep` when the work spans sessions.

## Attribution

- **Matt Pocock**: core skills framework and methodology
- **obra**: the Superpowers set, adapted for this workflow
- **Dietrich Gebert**: the ponytail family (lazy-code mode, review, audit, debt), MIT licensed. Source: https://github.com/DietrichGebert/ponytail

## Usage

Each skill folder contains a `SKILL.md` file with the instructions the assistant follows.
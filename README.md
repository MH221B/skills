# Development Workflow Skills

A collection of skills for an enhanced development workflow. These skills are primarily based on the work of **Matt Pocock** (the GOAT), with some additions from **obra's Superpowers** set (adapted with minor adjustments to fit this workflow).

## What Are These?

These skills are designed to be used with an AI coding assistant to enhance productivity across planning, debugging, prototyping, testing, and architecture work.

## Skills Included

### Planning & Design
- **brainstorming** — Explore requirements and design before implementation
- **writing-plans** — Create structured implementation plans for multi-step tasks
- **grilling** — Grill the user relentlessly about a plan, decision, or idea
- **grill-me** — Stress-test ideas through intensive questioning
- **grill-with-docs** — Grill against existing domain knowledge, creating ADRs and glossary as you go
- **implement** — Implement a piece of work based on a spec or set of tickets (uses `/tdd` where pre-agreed, then `/code-review`)

### Development & Debugging
- **tdd** — Red-green-refactor test-driven development
- **diagnosing-bugs** — Disciplined feedback-loop diagnosis for hard bugs and performance regressions
- **prototype** — Build throwaway prototypes to explore designs
- **resolving-merge-conflicts** — Resolve an in-progress git merge/rebase conflict

### Research
- **research** — Investigate a question against high-trust primary sources and capture findings as a Markdown file

### Code & Architecture
- **codebase-design** — Shared vocabulary for designing deep modules
- **improve-codebase-architecture** — Find refactoring opportunities and deepening paths
- **domain-modeling** — Build and sharpen the project's domain model (CONTEXT.md / ADRs)
- **code-review** — Review changes since a fixed point along Standards and design axes
- **write-a-skill** — Create new agent skills with proper structure

### Minimalism and code review
- **ponytail** — Make the agent write the smallest thing that works. It questions whether code needs to exist, reaches for the standard library before a custom abstraction, and cuts needless structure. Levels: lite, full (default), ultra.
- **ponytail-review** — Review a diff for over-engineering and list what to delete.
- **ponytail-audit** — Same as review, but across the whole repo instead of just the diff.
- **ponytail-debt** — Gather the `ponytail:` shortcuts you deferred into one ledger so they don't rot.

### Handoff
- **handoff** — Compact the current conversation into a handoff document for another agent to pick up
- **pickup** — Resume work in a new session from the newest handoff document

### Utilities
- **find-skills** — Discover and install available skills
- **caveman** — Ultra-compressed communication mode (~75% fewer tokens)
- **wait-what** — Stop and re-pitch when the last message didn't land
- **setup-matt-pocock-skills** — Set up the domain-docs convention (CONTEXT.md / ADRs) for the engineering skills
- **unslop** — Strip AI tells from any writing and put a human voice back in. No fluff, no filler, no corporate vocabulary.

## Attribution

- **Matt Pocock** — Core skills framework and methodology
- **obra** — Superpowers set (adapted for this workflow)

## Usage

Each skill folder contains a `SKILL.md` file with detailed instructions and usage guidelines.
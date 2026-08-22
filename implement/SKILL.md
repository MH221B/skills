---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

If the work came from the brainstorming and writing-plans skills, read what those produced first, if the files exist:

- Spec: `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` (from brainstorming)
- Plan: `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md` (from writing-plans)

Treat the spec as the source of truth for what's being built and the plan as the task order to follow. If neither file exists, work from the user's description or tickets directly.

If a prototype from the prototype skill preceded the work, use it as reference. Find it via a context pointer in the spec or plan, or by scanning the areas the plan touches for prototype-named files and folders (`*prototype*`, `*demo*`, or anything marked `PROTOTYPE, wipe me`). Read it before writing production code, follow the decisions it validated, and don't carry its throwaway sloppiness into the real code.

Use /tdd where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use /code-review to review the work.

Commit your work to the current branch.

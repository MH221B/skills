---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, docs they might need to check, and how to verify it works. Give them the whole plan as bite-sized tasks. DRY. YAGNI. Frequent commits unless the user opts out (not for plan docs).

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Save plans to:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- (User preferences for plan location override this default)

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans: one per subsystem. Each plan should produce working software on its own.

## Testing Strategy

Tests are not the default. Work is usually verified by running the code, running the existing test suite, or a manual check.

- Check what was agreed during brainstorming, or ask the user: do they want tests written at all?
- New tests are written **only when the user opts in**. When they do, prefer **test-after** (write tests once the code works); use test-first (TDD) only if the user explicitly asks for it: and in that case follow the tdd skill.
- Record the decision in the `**Testing:**` line of the plan header and shape each task's steps to match.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Implement the change" - step
- "Verify it works" - step (see Testing Strategy: run the command, existing tests, or a manual check)
- "Commit" - step (omit if the user opts out of commits)

**The only exception is opted-in TDD:** if the user explicitly requested test-first development, use the red-green shape instead: write the failing test, run it to confirm it fails, implement the minimal code, run it to confirm it passes, commit. Follow the tdd skill for this.

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** Implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Testing:** [How each task verifies its work. Default: run the code / existing test suite / manual check. Only list test-first steps if the user explicitly opted into TDD.]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`: only when the plan's Testing line includes tests

- [ ] **Step 1: Implement [feature]**

```python
def function(input):
    return expected
```

- [ ] **Step 2: Verify it works**

Run: [command that exercises the change, an existing test, or a manual check]
Expected: [what you should observe]

- [ ] **Step 3: Commit** (omit if the user opts out of commits)

```bash
git add src/path/file.py
git commit -m "feat: add specific feature"
```

> TDD variant: only when the plan's `**Testing:**` line says test-first: replace Step 1 with "Write the failing test", add a step running it to confirm it fails, then implement and run it to confirm it passes. Follow the tdd skill.
````

## No Placeholders

Every step must contain the actual content an engineer needs. These are **plan failures**: never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code: the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

## Remember
- Exact file paths always
- Complete code in every step: if a step changes code, show the code
- Exact commands with expected output
- DRY, YAGNI, frequent commits unless the user opts out

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check the plan against it. This is a checklist you run yourself: not a subagent dispatch.

**1. Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps.

**2. Placeholder scan:** Search your plan for red flags: any of the patterns from the "No Placeholders" section above. Fix them.

**3. Type consistency:** Do the types, method signatures, and property names you used in later tasks match what you defined in earlier tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

If you find issues, fix them inline. No need to re-review: just fix and move on. If you find a spec requirement with no task, add the task.

## Plan Document Handling

Do NOT commit plan documents. Plans are authored for review and execution, but should not be committed by the agent unless explicitly requested.

## Execution Handoff

After saving the plan, ask the user to verify it before proceeding:

**"Plan complete and saved to `docs/superpowers/plans/<filename>.md` (not committed). Please review the plan, then tell me any changes, or say 'start executing'."**

- Wait for user approval before starting execution.
- Once approved, execute tasks in this session sequentially.
- Pause for checkpoints and review after completing sections or complex tasks.

---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing plans

## Overview

Plans are produced in two passes, so the orchestrator spends its tokens on structure and decisions while the worker subagent writes the detail:

- **Pass 1, high-level plan (orchestrator):** goal, file map, ordered task list with acceptance criteria. No implementation code.
- **Pass 2, detail expansion (worker subagent):** reads the spec and the high-level plan, then expands the plan in place with the exact code, commands, and commit steps.
- **Delegated execution:** the orchestrator tells the worker subagent to read the spec and the plan and implement a task or range of tasks. Delegate by reference; never paste task content into prompts.

The finished plan must let a skilled developer with zero context for this codebase and problem domain implement each task without getting stuck. DRY. YAGNI.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Save plans to:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- (User preferences for plan location override this default)

## Scope check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans: one per subsystem. Each plan should produce working software on its own.

## Testing strategy

Tests are not the default. Work is usually verified by running the code, running the existing test suite, or a manual check.

- Check what was agreed during brainstorming, or ask the user: do they want tests written at all?
- New tests are written **only when the user opts in**. When they do, prefer **test-after** (write tests once the code works); use test-first (TDD) only if the user explicitly asks for it, and in that case follow the tdd skill.
- Record the decision in the `**Testing:**` line of the plan header and shape each task's steps to match.

## Pass 1: high-level plan (orchestrator)

### File structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure. But if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

### Task list

Write the ordered task list. Each task entry:

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py`
- Test: `tests/exact/path/test.py`, only when the plan's Testing line includes tests

**What:** 2-5 sentences on what this task does and the shape of the change.

**Done when:** acceptance criteria, observable and checkable.

**Depends on:** earlier task numbers, or "none, so it can run in parallel".
```

Rules for the high-level plan:

- Exact file paths always.
- No implementation code. The single exception: pin an interface when the decision itself matters (a function signature, a data schema, a config format) and mark it **Pinned** so the detail pass preserves it.
- Mark tasks that can run in parallel; everything else executes in order.

## Pass 2: detail expansion (worker subagent)

Dispatch the worker subagent:

> Read the spec at `[SPEC_FILE_PATH]` and the plan at `[PLAN_FILE_PATH]`. Expand the plan in place into a detailed version: for every task, replace **What** with concrete checkbox steps: the exact code for each change and the verify command with its expected output. Keep the task list, its order, and the file paths unchanged. Where the plan conflicts with the spec, flag it in the plan instead of silently resolving it.

Record the session ID this dispatch returns. Execution can continue this session instead of re-priming a fresh one.

The expanded plan must follow:

**Bite-sized task granularity.** Each step is one action (2-5 minutes): implement, verify. The only exception is opted-in TDD: if the plan's `**Testing:**` line says test-first, use the red-green shape instead (write the failing test, run it to confirm it fails, implement the minimal code, run it to confirm it passes) and follow the tdd skill for this.

**Expanded task format:**

````markdown
### Task N: [Component Name]

**Files:** [carried over from the high-level plan]

- [ ] **Step 1: Implement [feature]**

```python
def function(input):
    return expected
```

- [ ] **Step 2: Verify it works**

Run: [command that exercises the change, an existing test, or a manual check]
Expected: [what you should observe]
````

**No placeholders.** Every step must contain the actual content an engineer needs. These are **plan failures**: never write:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code: the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

**Remember:** exact file paths. Complete code in every step: if a step changes code, show the code. Exact commands with expected output. DRY, YAGNI.

## Plan document header

**Every plan starts with this header (written in Pass 1, preserved through expansion):**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** Read the spec and this plan, then implement your assigned tasks in order. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Testing:** [How each task verifies its work. Default: run the code / existing test suite / manual check. Only list test-first steps if the user explicitly opted into TDD.]

**Spec:** [path to the spec document this plan implements]

---
```

## Plan review

After the detail pass returns, check the expanded plan with fresh eyes:

1. **Spec coverage:** skim each spec requirement. Can you point to a task that implements it? List any gaps.
2. **Placeholder scan:** any pattern from "No Placeholders"? Fix them.
3. **Type consistency:** do the types, method signatures, and property names match across tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

Then dispatch `plan-document-reviewer-prompt.md` to a general-purpose subagent, replacing `[PLAN_FILE_PATH]` and `[SPEC_FILE_PATH]` with the actual paths. Fix any **Issues** it reports; **Recommendations** are advisory.

## Plan document handling

Do NOT commit plan documents. Plans are written for review and execution, but the agent does not commit them unless explicitly requested.

## Execution handoff

After the plan review, ask the user to verify before proceeding:

**"Plan complete and saved to `docs/superpowers/plans/<filename>.md` (not committed). Please review the plan, then tell me any changes, or say 'start executing'."**

- Wait for user approval before starting execution.
- First dispatch: tell the worker subagent: "Read the spec at `<spec path>` and the plan at `<plan path>`. Implement Tasks N-M. Follow the plan's steps and verification." If the Pass 2 expansion session is still available, continue it by session ID instead. It already holds the spec, plan, and codebase context, so the prompt is just "Continue: implement Tasks N-M."
- Reuse the worker session for sequential ranges: every dispatch returns a session ID; continue it ("Implement Tasks N-M next") rather than starting fresh. The worker keeps its context, skips re-reading the spec and plan, and the re-sent history bills mostly as prompt-cache reads. Start fresh only when the session is gone, the model changed, or it has drifted (stale file states, accumulated dead ends). Parallel task ranges always get separate sessions.
- After parallel ranges converge: continue the session whose work the next range builds on (same files or subsystem). It made those changes, so its view is current; name the files the other sessions modified so it re-reads them first. If the next range integrates several sessions' work, start fresh: each parallel session's memory of the others' files is stale, and a fresh worker reads the real current state.
- Plans have no commit steps. The worker implements and verifies; committing is decided outside the plan.
- Dispatch one task or a small contiguous range at a time. Dispatch independent tasks in parallel; keep dependent tasks in order.
- Do not micro-manage: no pasting task content or file dumps into the prompt, no re-reading every diff. Check a task off when the worker reports it done and its verification passed; spot-check only what is surprising.
- Pause for user checkpoints after completing sections or complex tasks.

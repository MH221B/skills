---
name: ponytail-review
description: >
  Review for over-engineering, in a diff or in a spec/plan document. Finds
  what to delete: reinvented standard library, unneeded dependencies,
  speculative abstractions, dead flexibility, features nobody asked for. One
  line per finding: location, what to cut, what replaces it. Use when the user
  says "review for over-engineering", "what can we delete", "is this
  over-engineered", "simplify review", "review this plan", "audit this spec",
  or invokes /ponytail-review. Complements correctness-focused review, this
  one only hunts complexity.
source: https://github.com/DietrichGebert/ponytail
---

Review a diff or a spec/plan document for unnecessary complexity. One line per finding: location, what to cut, what replaces it. The best outcome is the thing getting shorter.

## Format

`L<line>: <tag> <what>. <replacement>.`, or `<file>:L<line>: ...` for
multi-file diffs.

Tags:

- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` hand-rolled thing the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.

## Documents

The same lens works on a spec (`docs/superpowers/specs/...`) or a plan (`docs/superpowers/plans/...`) before it becomes code. The tags map over:

- `yagni:` a feature or section nobody asked for, a "future extensibility" tombstone
- `delete:` expected-soon stubs, "later" sections, placeholders planning to scaffold
- `shrink:` a task that touches five files where one suffices, a section twice as long as its idea
- `stdlib:` and `native:` don't apply to prose. Use "an existing codebase pattern already covers this" instead.

Document findings use the same one-line format, citing the section or line instead of a line-range.

## Examples

❌ "This EmailValidator class might be more complex than necessary, have you
considered whether all these validation rules are needed at this stage?"

✅ `L12-38: stdlib: 27-line validator class. "@" in email, 1 line, real validation is the confirmation mail.`

✅ `L4: native: moment.js imported for one format call. Intl.DateTimeFormat, 0 deps.`

✅ `repo.py:L88: yagni: AbstractRepository with one implementation. Inline it until a second one exists.`

✅ `L52-71: delete: retry wrapper around an idempotent local call. Nothing replaces it.`

✅ `L30-44: shrink: manual loop builds dict. dict(zip(keys, values)), 1 line.`

## Scoring

End with the only metric that matters: `net: -<N> lines possible.`

If there is nothing to cut, say `Lean already. Ship.` and stop.

## Boundaries

Scope: over-engineering and complexity only. Correctness bugs, security holes,
and performance are explicitly out of scope. Route them to a normal review
pass, not this one. A single smoke test or `assert`-based
self-check is the ponytail minimum, not bloat, never flag it for deletion.
Does not apply the fixes, only lists them.
"stop ponytail-review" or "normal mode": revert to verbose review style.

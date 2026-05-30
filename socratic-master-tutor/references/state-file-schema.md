# Learning State File Schema

Detailed specification for the persistent learning state files that track student progress across tutoring sessions.

## Overview

Each `.md` file represents one topic (e.g., `async-javascript.md`, `calculus.md`). Files are stored in:
```
tutoring-state/
├── [topic-name].md
└── [topic-name].md
```

**Naming convention:** Lowercase, hyphen-separated (e.g., `async-javascript`, `differential-equations`, `photosynthesis`).

## Full Schema

### Header Section

```markdown
# [Topic]: [Full Topic Title]

**Mode:** [Coding | General]
**Session Initiated:** YYYY-MM-DD HH:MM UTC
**Last Updated:** YYYY-MM-DD HH:MM UTC
```

**Fields:**
- `Mode` - **Coding** (software/algorithms) or **General** (math/history/science/other)
- `Session Initiated` - Date/time when learning on this topic began
- `Last Updated` - Most recent session date/time (update after each session)

---

## Section 1: Baseline Assessment

Captured in Phase 1 of first tutoring session. Do not update unless major reassessment occurs.

```markdown
## Baseline Assessment

- **Conceptual Understanding:** [Beginner | Intermediate | Advanced] + descriptor
- **Problem-Solving Ability:** [Description of approach]
- **Tool Fluency (if coding):** [Language, IDE, framework familiarity]
- **Confidence Level:** [1-10 scale, self-reported]
- **Learning Context:** [Why learning this—project, coursework, curiosity, etc.]
```

**Examples:**

*Coding Example:*
```markdown
## Baseline Assessment

- **Conceptual Understanding:** Beginner - knows JavaScript syntax but confused about async execution
- **Problem-Solving Ability:** Tries to solve by trial-and-error, doesn't form hypotheses
- **Tool Fluency (if coding):** Node.js, VS Code, familiar with promises but not async/await
- **Confidence Level:** 3/10 - frustrated by async bugs
- **Learning Context:** Building API client for work project, needs this to unblock feature
```

*General Example:*
```markdown
## Baseline Assessment

- **Conceptual Understanding:** Intermediate - can solve derivative problems with power rule but doesn't understand *why* it works
- **Problem-Solving Ability:** Procedural; applies formulas without connecting to real-world applications
- **Tool Fluency (if coding):** N/A
- **Confidence Level:** 5/10 - feels like just memorizing formulas
- **Learning Context:** Taking calculus for engineering degree, wants deeper understanding before integrals
```

---

## Section 2: Learning Goals

Specific, measurable outcomes defined in Phase 1. Can be updated as goals clarify.

```markdown
## Learning Goals

- Goal 1: [Specific outcome - what will they know/be able to do?]
- Goal 2: [Specific outcome]
```

**Examples:**

```markdown
## Learning Goals

- Understand async execution model (why does async/await not freeze the app?)
- Build API client that handles concurrent requests without race conditions
- Confidently debug async-related bugs without trial-and-error
- Explain async/await to teammates
```

---

## Section 3: Successful Mental Models

Analogies, frameworks, or explanations that "clicked" for the student. Essential for consistent teaching across sessions.

```markdown
## Successful Mental Models

*Analogies, frameworks, or explanations that resonated with this student:*

- **Model 1:** [Explanation] -> **Why it worked:** [What made this click]
- **Model 2:** [Explanation] -> **Why it worked:** [What made this click]
```

**Examples:**

```markdown
## Successful Mental Models

- **Restaurant analogy (async):** "You order food. The restaurant doesn't freeze while cooking—they serve other customers. You wait for YOUR food when it's ready." -> **Why:** Made abstract timing concrete; student immediately understood non-blocking behavior
- **Speedometer (derivatives):** "Like reading your speedometer—tells you speed *right now*, not total distance." -> **Why:** Grounded abstract calculus in driving experience they know
- **Branching timeline (history):** "Each event is a fork in the road. If Versailles didn't happen, would the Depression still lead to WWII?" -> **Why:** Helped student see cause-effect chains instead of isolated facts
```

**Usage:** Reference these models in future sessions. *"Remember the restaurant analogy? This is like that situation but with..."*

---

## Section 4: Identified Misconceptions & Fixes

Record incorrect thinking patterns and how you corrected them. Critical for preventing regression and accelerating future sessions.

```markdown
## Identified Misconceptions & Fixes

*Patterns of incorrect thinking, and how we corrected them:*

- **Misconception 1:** [What they believed] -> **Correction:** [How we helped them see the truth]
- **Misconception 2:** [What they believed] -> **Correction:** [How we helped them see the truth]
```

**Examples:**

```markdown
## Identified Misconceptions & Fixes

- **"async/await freezes the whole app"** -> **Correction:** Asked "What would happen to other users' requests?" Student realized only that function pauses, not the event loop
- **"Derivatives are just slope formulas"** -> **Correction:** Asked "Why do we care about slope at one point?" Led them to instantaneous rate of change
- **"Germany's problems were purely economic"** -> **Correction:** Asked "Why did people trust a dictator for help?" Made them connect economic desperation to psychological vulnerability
```

**Usage:** If student shows similar misconception again, reference it: *"We saw this before—remember why that thinking didn't work?"*

---

## Section 5: Pacing & Constraints

How this particular student learns best. Update as you discover preferences.

```markdown
## Pacing & Constraints

- **Preferred Learning Speed:** [Fast/Moderate/Deliberate] - description
- **Session Duration Preference:** [e.g., "30 min focused bursts" or "2 hour deep dives"]
- **Technical Environment:** [OS, IDE, language version, tools used]
```

**Examples:**

```markdown
## Pacing & Constraints

- **Preferred Learning Speed:** Moderate - likes time to think but gets frustrated with too many sub-questions
- **Session Duration Preference:** 45-minute focused sessions with breaks; loses attention after 90 min
- **Technical Environment:** MacBook, VS Code, Node.js v18, uses Chrome DevTools

---

- **Preferred Learning Speed:** Fast - prefers challenging questions, gets bored with over-explanation
- **Session Duration Preference:** Prefers 2-hour deep dives to short sessions
- **Technical Environment:** N/A (general tutoring)
```

---

## Section 6: Progress Over Time

Chronological log of sessions. Shows learning trajectory, breakthroughs, and areas of struggle.

```markdown
## Progress Over Time

*Chronological log of sessions, breakthroughs, and setbacks:*

- **Session N (YYYY-MM-DD):** [Summary: topic, breakthrough, challenge, next step]
- **Session N+1 (YYYY-MM-DD):** [Summary]
```

**Examples:**

```markdown
## Progress Over Time

- **Session 1 (2026-05-28):** Covered async execution model. Breakthrough: "Restaurant analogy" made it click. Student realized async doesn't freeze app. Next: promises vs. async/await
- **Session 2 (2026-05-30):** Worked through promise chains. Student struggled with multiple .then() callbacks—saw how async/await is syntactic sugar. Setback: confuses error handling in promises vs. async. Next: deep dive on try/catch vs. .catch()
- **Session 3 (2026-06-02):** Quiz mode on promises—75% accuracy. Gaps: Promise.all() and race conditions. Strength: understands promise states. Ready to tackle async patterns. Next: iterator/generator patterns
```

---

## Section 7: Quiz Performance Tracking

Detailed stats from Quiz Mode sessions. Shows mastery progression and identifies weak topics.

```markdown
## Quiz Performance Tracking

*Detailed stats from Quiz Mode sessions:*

- **Quiz N (YYYY-MM-DD):** Topic: [X] | Questions: [N] | Correct: [N] | Accuracy: [%] | Strengths: [what they got right] | Gaps: [what they missed]
- **Quiz N+1 (YYYY-MM-DD):** ...
```

**Examples:**

```markdown
## Quiz Performance Tracking

- **Quiz 1 (2026-05-30):** Topic: Async Execution Model | Questions: 5 | Correct: 4 | Accuracy: 80% | Strengths: Understood event loop, non-blocking | Gaps: Confused about microtask vs. macrotask queues
- **Quiz 2 (2026-06-02):** Topic: Promises | Questions: 6 | Correct: 5 | Accuracy: 83% | Strengths: Promise chaining, error handling | Gaps: Promise.all() edge cases, race conditions
- **Quiz 3 (2026-06-05):** Topic: Async/Await | Questions: 5 | Correct: 5 | Accuracy: 100% | Strengths: Everything | Gaps: None identified. Ready for advanced patterns.
```

---

## Section 8: Related Topics & Cross-Links

Connections to other topics in `tutoring-state/`. Enables relationship inference and topic sequencing.

```markdown
## Related Topics & Cross-Links

*Connections to other .md files for relationship inference:*

- **Depends On:** [Links to prerequisite topics] (must learn before this)
- **Prerequisite For:** [Links to advanced topics] (needed before learning those)
- **Reinforced By:** [Links to related topics] (patterns appear together, reinforce learning)
```

**Examples:**

*Coding Example:*
```markdown
## Related Topics & Cross-Links

- **Depends On:** javascript-fundamentals, event-loop
- **Prerequisite For:** promise-patterns, async-generators, reactive-programming
- **Reinforced By:** debugging-async, error-handling
```

*General Example:*
```markdown
## Related Topics & Cross-Links

- **Depends On:** basic-algebra, concept-of-limits
- **Prerequisite For:** integrals, differential-equations, optimization
- **Reinforced By:** physics-kinematics, economics-marginal-analysis
```

> **Note:** The cross-links in this section are the source of truth for topic relationships. `tutoring-state/knowledge-graph.md` is a **derived artifact** built from these fields — do not edit it manually. Run `scripts/generate-knowledge-graph.py` to rebuild it after any changes.

---

## Complete Example: Async JavaScript

```markdown
# Async JavaScript: Asynchronous Programming Fundamentals

**Mode:** Coding
**Session Initiated:** 2026-05-28 14:30 UTC
**Last Updated:** 2026-06-05 16:15 UTC

## Baseline Assessment

- **Conceptual Understanding:** Beginner - knows JavaScript syntax but confused about async execution model
- **Problem-Solving Ability:** Trial-and-error approach, doesn't form hypotheses about timing
- **Tool Fluency (if coding):** Node.js, VS Code, familiar with `.then()` but not async/await
- **Confidence Level:** 3/10 - frustrated by async bugs in API client
- **Learning Context:** Building API client for work project; needs this to unblock feature delivery

## Learning Goals

- Understand why async/await doesn't freeze the application
- Build API client that handles concurrent requests correctly
- Confidently debug async-related race conditions
- Explain async execution model to teammates

## Successful Mental Models

- **Restaurant Analogy:** "Order food. Restaurant doesn't freeze while cooking—serves other customers. You wait for YOUR food." -> Made timing concrete and non-blocking behavior intuitive
- **Event Loop Mental Model:** "Browser/Node queues tasks. Sync runs first, then microtasks (promises), then next task." -> Explains why await pauses function, not app
- **Speedometer Reading:** "Shows speed right now, not total distance traveled. Same with async—it's about what's happening at this moment." -> Connected to prior calculus learning

## Identified Misconceptions & Fixes

- **"async/await freezes the whole app"** -> Asked "What about other users' requests?" Student realized only that function pauses, event loop continues
- **"await always means wait"** -> Clarified "await pauses execution of that async function, but the browser continues handling other tasks. Event loop runs other code."
- **"I need async everywhere"** -> Discussed "Which operations actually take time? Network calls, file I/O, timers. CPU operations are fast—don't need async for those."

## Pacing & Constraints

- **Preferred Learning Speed:** Moderate - wants time to think but frustrated with over-simplification
- **Session Duration Preference:** 45-minute focused sessions; loses focus after 90 min
- **Technical Environment:** MacBook, VS Code, Node.js v18, uses Chrome DevTools

## Progress Over Time

- **Session 1 (2026-05-28):** Assessed baseline. Covered async execution model + event loop. Restaurant analogy clicked. Student understood non-blocking behavior. Next: promises
- **Session 2 (2026-05-30):** Worked through promise chains and `.then()`. Student struggled with nested callbacks—saw how async/await is syntactic sugar. Setback: error handling confusion (.catch() vs try/catch). Next: deep dive on error handling patterns
- **Session 3 (2026-06-02):** Quiz mode on async/await—80% accuracy. Gaps: microtask vs. macrotask queues, Promise.all(). Strengths: understands execution order. Ready for advanced patterns. Next: concurrent request handling
- **Session 4 (2026-06-05):** Built API client with concurrent requests. Student applied learning to real code. 100% confidence on this topic. Ready for advanced: generators, observables.

## Quiz Performance Tracking

- **Quiz 1 (2026-05-30):** Topic: Event Loop & Execution Model | Questions: 5 | Correct: 4 | Accuracy: 80% | Strengths: Non-blocking understanding, call stack | Gaps: Microtask queue internals
- **Quiz 2 (2026-06-02):** Topic: Promises | Questions: 6 | Correct: 5 | Accuracy: 83% | Strengths: Chaining, error handling | Gaps: Promise.all() edge cases, Promise.race()
- **Quiz 3 (2026-06-05):** Topic: Async/Await Patterns | Questions: 7 | Correct: 7 | Accuracy: 100% | Strengths: All patterns mastered | Gaps: None identified

## Related Topics & Cross-Links

- **Depends On:** javascript-fundamentals, event-loop, callbacks
- **Prerequisite For:** promise-patterns, reactive-programming, async-generators
- **Reinforced By:** debugging-async-code, error-handling-javascript
```

---

## Automation

**`scripts/create-state-file.py`** auto-generates this schema for new topics.

**`scripts/analyze-learning-patterns.py`** parses all state files to identify:
- Topic prerequisites (which must be learned first)
- Common misconceptions across learners
- Learning progression (time from beginner to mastery)
- Quiz performance trends


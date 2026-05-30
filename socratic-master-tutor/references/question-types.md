# Socratic Question Types & Examples

Five core question types used throughout Phase 3 (Execution & Progressive Questioning) and Phase 4 (Debugging). Learn to recognize and deploy each type based on student needs.

---

## 1. Clarifying Questions

**Purpose:** Surface assumptions and ensure shared understanding.

**When to use:**
- Student makes an assertion you want to verify
- Unclear what they mean
- Want to confirm their reasoning
- Testing if they've thought something through

**Pattern:** *"You said X—what reasoning led you to that conclusion?"*

### Coding Example

**Student:** "I think I should use a for loop for this."

**You (Clarifying):** "Walk me through why a for loop feels right here. What does the for loop give you that you need?"

**Expected outcome:** Student articulates their thinking (or realizes they haven't fully thought it through).

---

### General Example

**Student:** "World War II happened because of the Great Depression."

**You (Clarifying):** "So you're saying the Depression *caused* WWII? Help me understand—what's the mechanism? How does economic struggle lead to a world war?"

**Expected outcome:** Student realizes they've oversimplified and needs to think about human psychology, politics, nationalism.

---

## 2. Probing Questions

**Purpose:** Dig deeper, explore implications, test edge cases.

**When to use:**
- Student's answer is surface-level
- Want to expose complexity
- Test for real understanding vs. memorization
- Explore consequences

**Pattern:** *"What would happen if [X changed]?"* or *"What happens in this edge case?"*

### Coding Example

**Student:** "I'll use a global variable to track the count."

**You (Probing):** "Interesting. Now, what if this code runs in two different places at the same time? What would happen to your global variable?"

**Expected outcome:** Student realizes global state causes race conditions, discovers they need thread-safe approach.

---

### General Example

**Student:** "Plants need sunlight for photosynthesis."

**You (Probing):** "Right. But here's a question: what if a plant got zero sunlight? Could it do photosynthesis? Why or why not?"

**Expected outcome:** Student realizes sunlight is essential energy source, deepens understanding.

---

## 3. Connecting Questions

**Purpose:** Link concepts, show relationships, enable transfer learning.

**When to use:**
- Two topics relate but student hasn't noticed
- Want to build mental models that span domains
- Help transfer prior learning to new context
- Show patterns that repeat

**Pattern:** *"How does this relate to [prior topic we learned]?"* or *"This is like [X you already know], right?"*

### Coding Example

**Student:** "I'm confused about how async/await works."

**You (Connecting):** "You've used promises before, right? Remember how `.then()` lets you chain operations? async/await is just syntactic sugar for the same thing. How is that relationship useful to remember?"

**Expected outcome:** Student connects new concept to prior learning, reduces cognitive load.

---

### General Example

**Student:** "I don't understand why derivatives matter."

**You (Connecting):** "Think about velocity—how fast you're moving at one instant. That's a derivative! And remember in our last session how we talked about rates of change in economics? Derivatives show up everywhere. Can you think of other places where 'instantaneous rate' matters?"

**Expected outcome:** Student sees derivatives as a transferable pattern, not isolated formula.

---

## 4. Counter Questions

**Purpose:** Challenge thinking, expose contradictions, prompt reconsideration.

**When to use:**
- Student's logic has a flaw
- They're headed in wrong direction
- Want them to reconsider assumptions
- Testing if they've considered alternatives

**Pattern:** *"What if we flip it?"* or *"That's interesting, but what about [contradiction]?"*

### Coding Example

**Student:** "I'll store all the data in a single array."

**You (Counter):** "I see the appeal of simplicity. But what if you need to find one item by ID? How fast would that be with a single array?"

**Expected outcome:** Student realizes O(n) lookup is inefficient, considers data structures (hash table, tree) that optimize for their actual access pattern.

---

### General Example

**Student:** "Increasing taxes always hurts the economy."

**You (Counter):** "Interesting perspective. But I have a question: if zero taxes are best for the economy, why don't countries with no taxes have the strongest economies? What's happening there?"

**Expected outcome:** Student realizes the relationship is more nuanced—taxes fund infrastructure, education, etc. Begins to think in tradeoffs.

---

## 5. Hypothetical Questions

**Purpose:** Explore implications, test limits, build scenarios.

**When to use:**
- Want to test deep understanding in new context
- Exploring consequences and cascading effects
- Building intuition through scenarios
- Testing principles in edge cases

**Pattern:** *"If [hypothetical scenario], what would happen?"* or *"Imagine we changed [X]—what breaks?"*

### Coding Example

**Student:** "My code works for 100 items."

**You (Hypothetical):** "Great! Now imagine your database grew to 1 million items. Would your code still work? If not, where would it break first?"

**Expected outcome:** Student realizes performance characteristics change with scale, discovers need for indexing, caching, or different algorithms.

---

### General Example

**Student:** "The Treaty of Versailles humiliated Germany."

**You (Hypothetical):** "OK, so imagine the Treaty of Versailles had been gentler—still held Germany accountable but with smaller reparations and less resentment. Would we still have gotten WWII?"

**Expected outcome:** Student realizes Versailles was *one factor* among many, not the sole cause. Builds causal reasoning.

---

## Question Escalation Pattern

Start with clarifying (shallow), escalate to probing/connecting/counter (deeper), finish with hypothetical (deepest):

```
Student makes assertion
        [DOWN]
Clarify: "What did you mean?" (confirm understanding)
        [DOWN]
Probe: "What about edge case?" (test completeness)
        [DOWN]
Connect: "How does this relate to X?" (build mental models)
        [DOWN]
Counter: "But what about contradiction?" (challenge assumptions)
        [DOWN]
Hypothetical: "If context changed, would it still work?" (test principles)
```

**Don't jump straight to hypothetical.** Build foundation with clarifying first.

---

## Micro-Examples: Rapid-Fire Exchanges

### Coding: React Rendering

**Student:** "I'll add another useEffect to fetch data."

**You (Clarify):** "What will this new useEffect do differently than the one you already have?"

**Student:** "Oh... maybe it's the same? Let me think."

**You (Probe):** "Exactly. And here's another thought: what happens if both useEffects try to fetch at the same time?"

**Student:** "They'd both run... duplicate requests?"

**You (Counter):** "Right. So adding more useEffects might actually make the problem worse. What if instead we managed this with a single effect?"

**Student:** "I'd need to coordinate what gets fetched... one dependency array?"

**You (Hypothetical):** "Exactly! Now, imagine this component mounted and unmounted 100 times per second. What would happen with your approach?"

---

### General: History Causality

**Student:** "The economic crisis made people support Hitler."

**You (Clarify):** "When you say 'made people,' what's the mechanism? Does poverty automatically create fascists?"

**Student:** "No, but desperation makes them vulnerable..."

**You (Probe):** "Vulnerable to what, specifically? What was Hitler offering them?"

**Student:** "A solution. Hope. Blame for the problems."

**You (Connect):** "So like we talked about before with psychological needs—people need to feel secure and have purpose. Hitler provided that narrative?"

**Student:** "Yes! That's the link I was missing."

**You (Counter):** "But here's a harder question: why didn't other countries with depressions fall to dictators at the same time? What's different?"

**Student:** "Different... political cultures? Institutions?"

**You (Hypothetical):** "Exactly! So imagine Germany had stronger democratic institutions. Would the same desperation still lead to dictatorship?"

---

## Anti-Examples: What NOT to Do

### [ERROR] Interrogation (Too many questions, too fast)

**Bad:**
> "What do you mean? Why did you think that? Have you considered X? What about Y? Doesn't that contradict Z?"

**Problem:** Student feels attacked, shuts down. Loses thread.

**Better:** Ask one question, wait for response. Then ask next question.

---

### [ERROR] Rhetorical Questions (You're not actually asking)

**Bad:**
> "Don't you think that's inefficient?" (You already know the answer and are lecturing)

**Problem:** Student recognizes it's rhetorical, doesn't engage with thinking.

**Better:** "What would happen if we had 1 million items? Would this still work?" (Genuine question you're curious about their answer to)

---

### [ERROR] Leading Questions (Forcing answer you want)

**Bad:**
> "You do realize that global variables are bad, right?" (Answer is implied)

**Problem:** Student agrees to end discussion, doesn't explore thinking.

**Better:** "What would happen if this code ran in two places at the same time?" (Student discovers the problem)

---

### [ERROR] Gotcha Questions (Ambush)

**Bad:**
> "So async/await is just syntactic sugar for promises, right? Then why can't you use async/await in older Node.js?" (Trick question)

**Problem:** Student feels trapped. Fails not from lack of understanding but from ambush.

**Better:** "Async/await is newer syntax. What do you think would happen if you tried to run it in very old Node.js?" (Genuine exploration)

---

## Combination in Real Tutoring

Most effective tutoring combines multiple question types in a single exchange:

```
Student: "I'll use a callback to handle the async response."

You: "Interesting approach. [CLARIFY] What would you pass to the callback?"

Student: "The data that came back."

You: "Right. [PROBE] Now, what if you had multiple async operations that depended on each other—chain them with callbacks?"

Student: "Yeah, I'd nest them..."

You: "Exactly. [CONNECT] Remember the pyramid of doom we talked about? That's what happens. [COUNTER] So what if we used promises or async/await instead?"

Student: "The code would be flatter?"

You: "[HYPOTHETICAL] Perfect. Now imagine 5 levels of nesting. How readable is that compared to async/await?"

Student: "Oh! I see why you'd want async/await now."
```

---

## Tips for Question Mastery

1. **Ask one question at a time.** Never ask three questions in one breath.

2. **Wait for the answer.** Silence means they're thinking. Don't rush.

3. **Listen to their answer completely** before asking the next question. You might learn something that changes your direction.

4. **If they say "I don't know":** Break into smaller sub-questions (usually clarifying) rather than probing deeper.

5. **Match energy.** If they're frustrated, start with gentle clarifying. If they're overconfident, use counter/hypothetical.

6. **Reference prior learning.** Use connecting questions to link to what they already know.

7. **Celebrate discoveries.** When they figure it out from your question: *"Exactly! You just discovered it yourself."*

---

## Question Type Decision Tree

Use this to pick the right question:

```
Student gives response
    [DOWN]
Is it unclear what they mean?
    YES -> Ask CLARIFYING question
    [DOWN]
Is their answer surface-level or missing nuance?
    YES -> Ask PROBING question
    [DOWN]
Does this relate to prior learning?
    YES -> Ask CONNECTING question
    [DOWN]
Is there a flaw in their logic?
    YES -> Ask COUNTER question
    [DOWN]
Want to test if principle transfers to new context?
    YES -> Ask HYPOTHETICAL question
    [DOWN]
Otherwise: Praise, deepen with harder probing, or move to next phase
```


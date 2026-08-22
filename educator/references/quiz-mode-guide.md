# Quiz Mode: Complete Workflow Guide

Comprehensive guide for activating and executing Quiz Mode—active recall testing with adaptive difficulty and Socratic feedback.

---

## When to Activate Quiz Mode

User explicitly requests:
- *"Quiz me on X"*
- *"Test my understanding of Y"*
- *"Let's do a quiz on [topic]"*
- Or after tutoring: *"I think I've got it. Can you quiz me?"*

---

## Complete Quiz Workflow

### Phase 1: Topic Selection & Baseline Review

**Objective:** Confirm topic focus and assess current knowledge state.

#### Step 1a: Confirm Topic(s)

If student specified topic(s):
> "Got it—let's quiz on [topic]. Before we start, I want to make sure I'm covering the right material. Sound good?"

If student didn't specify:
> "I can quiz you on any topics we've learned together: [list from state files]. Which one(s) should we focus on? Or do you want a mix?"

#### Step 1b: Review Prior Learning

If state file exists for this topic:
> "Before we start, let me check where we left off. [Skim state file.] Based on our last session, here's what I think you understand well: [Strengths from prior quiz]. Here's where you seemed less certain: [Gaps from prior quiz]. Should we focus on those gaps, or do a fresh comprehensive quiz?"

If no state file:
> "This is new territory. Before quizzing, I'll ask: what's your current level on [topic]? Are we starting from basics, or testing intermediate/advanced understanding?"

#### Step 1c: Set Expectations

> "Here's how this works: I'll ask one question at a time—free-response, not multiple-choice. I'll adapt the difficulty as we go. If you get stuck, I'll ask guiding questions instead of just telling you the answer. We'll probably do 5–8 questions, depending on how it goes. Ready?"

---

### Phase 2: Question Design & Delivery

**Objective:** Deliver well-calibrated free-response questions that test deep understanding.

#### Question Characteristics

**[OK] Good Questions:**
- Free-response (require generation, not recognition)
- Test concepts, not syntax/trivia
- Have clear right/wrong answers (or range of acceptable answers)
- Build from foundational to advanced
- Connect to real-world context

**[ERROR] Bad Questions:**
- Multiple-choice (tests recognition, not recall)
- Gotcha/trivia (syntax, obscure edge cases)
- Vague (unclear what a correct answer is)
- Batch questions (5 at once)
- Disconnected from application

#### Question Types & Examples

**Explain in Your Own Words**
- "Explain [concept] as if you're teaching someone who just started learning."
- "In your own words, what is [X] and why does it matter?"

*Example (Async JS):* "Explain the event loop. Why doesn't async/await freeze the application?"

**Approach/Strategy**
- "How would you approach [problem]?"
- "Walk me through your strategy for solving [X]."

*Example (Architecture):* "You're building a monolith that's growing slowly. Walk me through how you'd decide whether to break it into microservices."

**Edge Cases & Scenarios**
- "What would happen if [edge case]?"
- "Here's a scenario: [situation]. How would you handle it?"

*Example (Derivatives):* "You have a function that's discontinuous at one point. Can you take the derivative there? Why or why not?"

**Comparison & Tradeoffs**
- "Compare [X] and [Y]."
- "What are the tradeoffs between [approach A] and [approach B]?"

*Example (OOP):* "Compare inheritance and composition. When would you use each?"

**Why Questions**
- "Why does [this pattern] matter?"
- "Why would [method] be better than [alternative]?"

*Example (History):* "Why did the Great Depression make people receptive to dictators, whereas poverty in some other countries didn't have the same effect?"

---

### Phase 3: Adaptive Difficulty Scaling

**Key Principle:** Difficulty adjusts based on responses, not on predetermined sequence.

#### Difficulty Levels

**Foundational (Easy)**
- Tests core concept with simple example
- No edge cases
- "What is X?" or "Explain Y"

*Example:* "What is a promise in JavaScript?"

**Applied (Medium)**
- Tests concept in realistic scenario
- May include one edge case
- "How would you use X to solve Y?"

*Example:* "You need to make 3 API calls in sequence, with each depending on the previous. How would you approach this with async/await?"

**Advanced (Hard)**
- Tests synthesis, edge cases, principles
- Multiple considerations
- "Design a system that handles X, Y, Z constraints"

*Example:* "Design an error-handling strategy for concurrent API requests where each request has different retry policies. How do you handle cascading failures?"

#### Scaling Logic

| Response Quality | Next Question |
|:---|:---|
| **Correct (100%)** | Increase difficulty. Test synthesis, edge cases, or principles. |
| **Mostly Correct (80-90%)** | Pinpoint the 20% gap. Ask follow-up to complete understanding. Then increase difficulty slightly. |
| **Partial (50-80%)** | Ask simpler question on foundational concept beneath this one. Rebuild understanding. |
| **Incorrect (<50%)** | Go back one difficulty level. Test understanding of prerequisite concept. |
| **"I don't know"** | Break into 2-3 smaller foundational questions. Rebuild confidence. |

#### Examples of Scaling

**Escalation:**
```
Q1 (Foundational): "What is async/await?"
Student: [Perfect answer]

Q2 (Applied): "Design an API client that fetches user data, then their posts, then comments on those posts."
Student: [Good answer, misses error handling]

Q3 (Advanced - same difficulty): "Now add error handling where if user fetch fails, abort everything. If post fetch fails, show partial data."
Student: [Correct]

Q4 (Advanced - harder): "Scale this to 10,000 concurrent requests with rate limiting. How does your approach change?"
```

**De-escalation:**
```
Q1 (Applied): "Design an async function that fetches data and handles errors."
Student: "Uh... I'm not sure."

Q2 (Foundational): "What's the difference between a promise and async/await?"
Student: [Correct but basic]

Q3 (Applied - lower level): "Now write a simple async function that fetches data. What would error handling look like?"
Student: [Correct]

Q4 (Applied - same level): "Good! Now, what if the fetch times out after 5 seconds?"
```

---

### Phase 4: Socratic Feedback Loop

**Key Principle:** For incorrect/incomplete answers, use questions to guide self-correction BEFORE revealing the answer.

#### Response Handling

**Correct (100% accurate, well-reasoned)**

```
You: "Exactly right. You demonstrated deep understanding of [concept].
     Now here's a harder one: what if we had [edge case]?"
```

No need to over-praise or over-explain. Acknowledge and move to next question.

**Mostly Correct (80-90%, missing nuance or edge case)**

```
You: "You're 80% there. You got [correct part] perfect.
     I noticed you didn't mention [missing part].
     Walk me through what would happen in [scenario] with your approach."
```

Let them discover the gap. Only explain if they can't figure it out after your question.

**Partially Correct (50-80%, fundamental confusion)**

```
You: "I see where you're going. You got [correct part] right.
     But let me ask this: in your approach, what happens when [edge case]?
     Walk me through that scenario step-by-step."
```

Ask them to trace through their logic on a specific case. They'll often spot the flaw.

**Incorrect (<50%, fundamental misunderstanding)**

```
You: "Interesting approach. Let me ask a simpler question to clarify:
     [Ask foundational question about prerequisite concept]
     Once we nail that, we'll come back to this."
```

Drop back to foundational level. Don't correct directly.

**"I don't know"**

```
You: "That's OK. Let me break it down. What's the [basic component]?
     Just focus on that piece first."
```

Isolate the simplest piece. Success on small piece builds confidence.

#### Anti-Patterns (Forbidden)

[ERROR] **Instant Correction:**
```
You: "Wrong. The answer is X because Y."
```
Student feels judged, stops engaging, doesn't learn why they were wrong.

[OK] **Instead:**
```
You: "Interesting. Let me ask—what would happen if [scenario]?
     Walk me through that with your approach."
```

---

[ERROR] **Gotcha Responses:**
```
You: "Well, actually, in ES2023, that changed. You're wrong."
```
Student feels trapped by trivia, not testing their understanding.

[OK] **Instead:**
```
You: "Good reasoning! That approach works in older JavaScript.
     What if we could use [newer feature]? How would that change your design?"
```

---

[ERROR] **Semantic Pedantry:**
```
You: "You said 'initialize' but the correct term is 'instantiate'. Incorrect."
```
Student used different vocabulary but demonstrated understanding.

[OK] **Instead:**
```
You: "Perfect! You instantiated the class—that's exactly right.
     Now, what happens if you instantiate it twice?"
```

---

[ERROR] **Batch Quizzing:**
```
You: "Here are 5 questions. Answer them all."
```
Student can't focus, can't get feedback/adapt difficulty.

[OK] **Instead:**
```
You: "Here's question 1. [Wait for answer.]
     Based on that, here's question 2."
```

---

### Phase 5: Progress Tracking & Adaptive Routing

**Objective:** Track performance and identify topics for future review.

#### During Quiz: Running Tally

Keep track as you go:

| Question | Topic | Result | Notes |
|:---|:---|:---|:---|
| Q1 | Async Execution | [OK] Correct | Understood event loop |
| Q2 | Error Handling | [WARNING] Partial | Got try/catch but missed Promise.catch() |
| Q3 | Concurrent Requests | [ERROR] Incorrect | Confused Promise.all() with Promise.race() |
| Q4 (foundational) | Promise Basics | [OK] Correct | Redirected to foundation, now solid |
| Q5 | Concurrent Requests (retry) | [WARNING] Partial | Better, but still fuzzy on .race() |

#### End of Quiz: Summary

After final question:

```
You: "Let's wrap up. Here's what I saw:

Strengths:
- Event loop understanding: solid
- Error handling with try/catch: solid
- Async/await syntax: mastered

Areas to review:
- Promise.all() vs Promise.race()—that was the tricky one
- Error handling with nested promises

Next steps: You're ready for advanced async patterns (generators, streams).
But before that, do you want to spend 5 minutes on Promise.race() to nail it?"
```

---

### Phase 6: Quiz Conclusion & State File Update

**Objective:** Document results and identify next learning direction.

#### Update State File

Add to `## Quiz Performance Tracking`:

```markdown
- **Quiz N (YYYY-MM-DD):** Topic: [X] | Questions: [N] | Correct: [N] | Accuracy: [%] 
  | Strengths: [what they mastered] | Gaps: [what needs review] | Readiness: [beginner|intermediate|advanced]
```

#### Offer Next Steps

**If mastery demonstrated (85%+ accuracy, strong reasoning):**
> "You've clearly mastered this. Ready to move to the next topic, or dive into advanced applications?"

**If gaps identified (60-85% accuracy):**
> "You're close. The main gap is [topic]. Want to do a short tutoring session on that before you forget, or tackle it next time?"

**If foundational gaps (< 60% accuracy):**
> "We've identified some gaps at the foundation. Let's do another tutoring session focused on [topic] before quizzing again. This will help it stick."

---

## Complete Example: OOP Quiz Session

```
=== QUIZ MODE: Object-Oriented Programming ===

PHASE 1: Setup
─────────────
You: "Great! Let's quiz on OOP. Based on our last session, you mastered 
      classes and inheritance. You were less certain about polymorphism 
      and interface design. Should we focus on those?"

Student: "Yeah, polymorphism confused me."

You: "Perfect. We'll focus on that but mix in some easier questions too
     to build confidence. I'll ask one free-response question at a time.
     Ready?"

Student: "Ready!"

─────────────────────────────────────────────────────────────────────

PHASE 2-3: Questions with Adaptive Difficulty
──────────────────────────────────────────────

Q1 [Foundational - Applied]:
You: "Explain polymorphism. What does it mean and why does it matter
     in object-oriented design?"

Student: "It means objects can have the same interface but different
         implementations. Like different animals have a move() method
         but they move differently."

You (assessing): Strong answer. Move to applied level.

─────────────────────────────────────────────────────────────────────

Q2 [Applied]:
You: "Good explanation! Now, imagine you're designing a game with
     different weapon types: Sword, Bow, Gun. Each has a fire() method,
     but they behave differently. Walk me through how you'd structure
     this using polymorphism."

Student: "I'd... create a Weapon interface? And each weapon implements
         it differently?"

You (Socratic question): "Exactly! Now here's the question: if you have
a player holding an array of Weapons, how do you handle firing all of
them without knowing what type each is?"

Student: "Oh! I'd just call fire() on each and trust that the right
         one gets called..."

You: "Exactly! That's polymorphism in action. You move to next question."

─────────────────────────────────────────────────────────────────────

Q3 [Advanced]:
You: "Perfect. Now here's a harder one. You're designing a UI framework.
You have Button, Checkbox, Dropdown—all different widgets. They all have
render() and handleEvent(). But some can be nested, some can't. Some
fire events, some don't. How do you handle this complexity while
maintaining polymorphism?"

Student: "Hmm... I could create a base Widget interface with render()
         and handleEvent()..."

You (counter): "That gets you part way. But what about the 'nestable'
vs 'not nestable' part? How do you prevent someone from putting a
Button inside another Button if that doesn't make sense?"

Student: "Oh! Maybe I need multiple interfaces? Like NestableWidget
         and NonNestableWidget?"

You: "There we go! Or composition—a widget can have a 'children'
     property only if it's a Container. Great thinking."

─────────────────────────────────────────────────────────────────────

Q4 [Applied - lower, due to struggle on Q3]:
You: "You're doing great. Let me pivot slightly. Explain the Liskov
     Substitution Principle in your own words. Why is it important?"

Student: "Uh... something about inheritance?"

You (asking foundational question): "Let me rephrase: If you have a parent
class Animal and subclasses Dog and Penguin, what should be true about
the subclasses? What does Liskov say should always work?"

Student: "They should be usable anywhere the parent is used?"

You: "Exactly! So if code expects an Animal to fly(), and you pass a
     Penguin... what happens?"

Student: "Oh! It breaks! Penguin can't fly, so it violates Liskov."

You: "Right. That's why Liskov matters. Good recovery!"

─────────────────────────────────────────────────────────────────────

PHASE 5-6: Closure & Update
────────────────────────────

You: "Let's wrap up. Here's what I saw:

Strengths:
  [OK] Polymorphism concept: solid
  [OK] Interface design: strong reasoning
  [OK] Liskov Substitution Principle: understood after clarification

Gaps:
  [WARNING]  Complex interface hierarchies—struggled when constraints conflict
  [WARNING]  First instinct wasn't composition vs inheritance tradeoff

Quiz Stats: 4 questions, 3 correct, 75% accuracy

Next: You're ready for design patterns (Factory, Adapter, etc.) that
build on polymorphism. But before that, want to quickly reinforce
composition vs inheritance? 15 minutes?"

Student: "Yeah, let's do it before I forget."

You: "Perfect. [Shift back to Tutoring Mode for 15 min, then re-quiz if time]"

[State file updated with quiz results, gaps identified, next steps noted]
```

---

## Tips for Effective Quiz Mode

1. **One question at a time.** Never ask multiple questions in one response.

2. **Wait for answers.** Even if it's silent, they're thinking. Don't fill silence.

3. **Listen fully.** Their answer tells you about their understanding. Listen for reasoning, not just correctness.

4. **Adapt difficulty.** If they ace it, go harder. If they struggle, go foundational. Don't follow a predetermined sequence.

5. **Use follow-up questions.** For partial answers, ask follow-ups before moving to next question.

6. **Celebrate discoveries.** When they figure it out: *"You just discovered it yourself!"*

7. **Track as you go.** Keep a running tally so you have data for the summary.

8. **End on success.** If possible, end quiz with a question they can ace—builds confidence for future learning.

9. **Update state file.** Immediately after quiz, update state file with performance metrics and gaps. This matters for next quiz.

10. **Offer continuity.** *"Based on these gaps, want to do a short tutoring session to shore this up?"* Connects quizzing back to learning.


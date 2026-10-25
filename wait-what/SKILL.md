---
name: wait-what
description: "Stop. That last message did not land: re-pitch it."
disable-model-invocation: true
---

Wait, I don't understand where you've got to here.

Re-pitch the last message so I can follow it:

1. **Context first.** Say what we were doing and why this step exists. Two or three sentences. Assume I lost the thread several messages back.
2. **Plain words.** Talk in ASD-STE100 Simplified Technical English. Short sentences. Active voice. One idea per sentence. No metaphor, no invented nouns, no marketing.
3. **Our words.** Use the project's own terms for things. Check these files, in this order, and use the first ones that exist:
   - `CONTEXT.md` — use its vocabulary.
   - `CONTEXT-MAP.md` — follow it to the right one.
   - `AGENTS.md` or `CLAUDE.md` — use the names and house rules it gives.

   If none of them exist, use the terms the code, the file names, and my own messages already use. Do not invent new ones. If a thing has no name yet, say so in one line.
4. **Same facts, less noise.** Do not add claims, do not add work, do not apologise. Restate. Same content, reachable.

Then stop. Do not continue the task until I say go.

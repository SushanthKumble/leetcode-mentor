# Problem-Solving Workflow

The 10-step Practice Mode workflow. Ask one question at a time and don't advance until the gate is met.

## Contents

1. Understand the problem
2. Work through examples
3. Develop brute force
4. Identify bottlenecks
5. Pattern recognition
6. Derive the optimized algorithm (6b. Pseudocode)
7. Implementation
8. Testing and dry run
9. Complexity analysis
10. Post-solve reflection
- Getting a stuck user moving
- Calibrating to the user

---

## 1. Understand the problem

**Goal:** the user can restate the problem precisely, without any algorithm in mind.

If the problem is only named ("do Two Sum") and you are not certain of its exact current statement and constraints, ask the user to paste it. Never paraphrase a problem from memory as if it were authoritative.

Ask these, one at a time. Skip any the user has already answered well:

- "In your own words, what are we given?" (types, sizes, sorted or unsorted, can values repeat, can they be negative?)
- "What exactly do we return?" (a value, indices, a list, a boolean; does order matter; can there be several valid answers?)
- "What do the constraints tell you?" Push on this. `n ≤ 10^5` means roughly O(n log n) or better. `n ≤ 20` hints that exponential time is acceptable. Value ranges affect overflow and whether counting arrays are possible.
- "What does Example 1 show that the statement doesn't say outright?"
- "What edge cases could break a naive solution?"

**Gate:** input, output, and key constraints are correct. If the user misreads something (for example, thinking indices must be sorted, or missing that the array is sorted), fix it now with a question that exposes the gap: "Look at Example 2's output. Does that match what you said?"

**Do not:** hint at the technique, mention data structures, or say "this is a classic X problem".

## 2. Work through examples

**Goal:** the user builds intuition by hand and owns at least one edge case.

- "Trace Example 1 by hand. What would *you* do step by step, as a human?"
- "Make up the smallest valid input. What's the answer?"
- Then pick whichever of these are relevant and ask for **one** at a time: empty input (if allowed), all-duplicate values, negatives, already sorted, reverse sorted, a single element, the maximum size, values at the limits, no valid answer.

**Gate:** the user traced at least one example themselves and proposed at least one edge case with its expected output. Don't do every example for them. You may trace one *after* theirs to contrast.

**Watch for:** a manual trace that already contains the optimal idea ("I'd remember what I've seen"). Note it silently and come back to it in step 4.

## 3. Develop brute force

Ask: **"What is the simplest way you can solve this, even if it is inefficient?"**

Help the user:
- Describe the logic in plain words.
- Name the loops and operations.
- Check correctness on their edge cases.
- Derive time and space complexity.

**If the brute force is incorrect:** don't fix it. Give a counterexample, or ask them to run their idea on a specific input you know fails: "Try it on `[3, 3]` with target 6. What does it return?" Let them repair it.

**If they can't find one,** shrink the question:
- "Forget efficiency. If you could check *every* possibility, what would a 'possibility' be?" (a pair, a subarray, a subset, a path)
- "How would you list all of them?"
- "For one possibility, how do you check whether it's valid?"
- "Can you do it for n = 3 by hand?"

**If they jump straight to an optimal idea:** ask them to state the brute force in one sentence anyway, with its complexity. It is the baseline for explaining *why* the optimization matters in interviews. Don't make them code it.

**Gate:** a correct brute force with justified time and space complexity.

## 4. Identify bottlenecks

**Goal:** the user discovers *where* the waste is before they know the fix.

Ask the most relevant question first, one at a time:
- "Which line or loop dominates the cost?"
- "Are we repeating work? What does the inner loop recompute that a previous iteration already knew?"
- "Are we searching for something over and over? Could the answer to that search be ready in advance?"
- "As you scan left to right, what is the minimum you'd need to *remember* so you never look back?"
- "Would a different data structure make the slow operation cheap?"
- "Does sorting, or the input already being sorted, give us anything?"

**Gate:** the user names the redundant work in their own words, for example "for each element I rescan the whole array to find its complement".

**Do not** name the pattern here. "You're repeating a lookup" is fine. "Use a hash map" is a Level 3 hint and costs a hint.

## 5. Pattern recognition

Only after steps 3–4. Ask: "Which tool can store or answer that repeated thing cheaply?" Let the user propose one.

When a pattern fits, make the user articulate, one question at a time, the six points in [patterns.md](patterns.md):
1. What clues in *this* problem suggest it?
2. What conditions make it applicable here?
3. Why does it work here? (the invariant)
4. What does the general template look like?
5. When would it *not* work? (a small change to the problem that breaks it)
6. What alternative could also solve it, and what does that alternative cost?

Don't force a pattern. If a problem is mostly simulation or math, say so. If two patterns both work (for example hashing versus sort plus two pointers), have the user compare their trade-offs.

**Gate:** the user can say *why* the technique removes the bottleneck from step 4.

## 6. Derive the optimized algorithm

Ask: "Explain the algorithm in plain English, as if to a teammate. No code."

The explanation must cover:
- the main idea (one sentence)
- the data structures and what each holds
- the steps
- why it is correct (the invariant, or why no candidate answer is skipped)
- time and space complexity

If something is missing, ask for only that piece: "What does your map store, exactly, key → value?" If it's wrong, give a failing input.

**Gate:** a complete, correct plain-English algorithm. For Hard problems, also require an argument for correctness, such as an exchange argument for greedy, a recurrence plus base cases for DP, or a monotonic predicate for binary search on the answer.

### 6b. Pseudocode (the user writes it)

Ask: "Now turn that into pseudocode. No language syntax, just the structure: variables, loops, conditions, returns."

Check the pseudocode against the plain-English algorithm:
- Are all the data structures initialized?
- Is each loop's range right, and is the loop condition the invariant they described?
- Are the update order and the edge-case handling right (empty input, nothing found)?
- What's returned, and is it returned in every path?

Report **one** problem at a time with a failing input, as with code. Keep the user's style: any clear pseudocode is fine. Only ask for more structure if a line is ambiguous ("What exactly does 'shrink the window' do to `left` and to the set?").

**Gate:** correct pseudocode, written by the user. It becomes the reference for step 7: if the code and the pseudocode disagree, that's the first thing to point out. Save the final pseudocode in the log entry.

If the user asks *you* to write the pseudocode, that's hint level L5. Log it as such.

## 7. Implementation

"Go ahead and write it in [language]. Paste it when ready."

When code arrives:
1. Does it implement *their* algorithm from step 6? If not, point out where it diverges.
2. Are there logic errors? Report **one** issue at a time, most severe first. Name the region and give a failing input or a question, not the fix.
3. Let them fix it, then re-check.
4. Mention style issues (naming, dead code) only after the code is correct, and briefly.

Don't rewrite their code. If they explicitly ask for the full code, provide it, explain each part, and log it as a reveal.

If the user wants to code in an unfamiliar language, help with syntax questions directly. Syntax is not the skill being trained.

## 8. Testing and dry run

- "Dry-run your code on Example 1. Tell me the variable values at each iteration." For long inputs, the first few iterations are enough.
- Then ask for one case at a time from the user's own edge cases, plus a boundary case (min and max size, extreme values) and an adversarial case: the input most likely to break *this* algorithm, such as all-equal values for a window, a strictly decreasing array for a monotonic stack, or a disconnected graph for BFS.
- If tools are available and the user agrees, you may run their code on these tests. Report actual results only.

**Gate:** the user's dry run is correct and their edge cases pass.

## 9. Complexity analysis

The user computes, and must justify:
- **Time:** what is the basic operation, and how many times does it run? For amortized cases, why can each element be pushed or popped at most once?
- **Space:** total, and **auxiliary** (excluding input and output).
- **Worst case:** which input triggers it? Do hash operations degrade? How deep can recursion go, and does that cost stack space?

Reject hand-waving. "Why is that loop O(n) total when it's nested inside another loop?" is a fair challenge whenever it applies.

## 10. Post-solve reflection

1. Ask first: **"In one or two sentences, in your own words: what's the key idea you'd want to remember from this problem?"** Wait for the answer. Correct or sharpen it if needed.
2. Ask: "What clue in the problem would tell you to try this next time?"
3. Then write the summary (keep it concise):

```markdown
### <Number>. <Title> (<Difficulty>)
- **Pattern:** ...
- **Key observation:** ...
- **Brute force:** ... (time / space)
- **Optimized:** ... (time / space)
- **Pseudocode:**
  ```
  <the user's final, corrected pseudocode>
  ```
- **Mistake I made:** ...
- **Remember:** <user's own words>
- **Recognize it next time by:** ...
- **Outcome:** <independence level> (score N) · max hint level: L?
```

4. Update the log (see [progress-tracking.md](progress-tracking.md)). Mark the problem *Solved*, not *Mastered*. Mastery needs a later revision.
5. Offer **one** next step: a variation, a revision that's due, or the next problem. Don't give a list.

---

## Getting a stuck user moving

"I'm stuck" or a long silence (the user says they've been at it for 15+ minutes) does not automatically mean "give a hint". First diagnose, with one question:

- "What have you tried so far, and where exactly did it stop working?"

Then:
- If they don't know the **data structure or topic itself** (for example, "what's a linked list?"), pause the problem and run a primer from [concept-primers.md](concept-primers.md). That isn't a hint.
- If they're stuck on **understanding**, go back to step 1 or 2 with a concrete small example.
- If they're stuck on **finding any solution**, use the step 3 shrinking questions.
- If they're stuck on **optimization**, use a step 4 question.
- If they asked for a hint, or are still stuck after that, give the **next** hint-ladder level.

Long stuck time is normal. Remind them, once and briefly, that productive struggle is how this gets learned, then help. Don't lecture.

## Calibrating to the user

- **Skip what they've shown they can do.** If someone has solved 10 sliding-window problems independently, don't make them recite the template. Ask only what this problem adds.
- **Lean in where they're weak.** If the log shows a pattern of complexity mistakes, spend extra time on step 9.
- **Don't re-explain** a concept they explained correctly earlier in the session.

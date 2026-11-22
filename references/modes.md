# Modes: Solution, Review, Pattern Learning, Revision

Practice Mode is in [problem-solving-workflow.md](problem-solving-workflow.md), Hint Mode in [hint-ladder.md](hint-ladder.md), and Interview Mode in [interview-mode.md](interview-mode.md).

## Contents
- Solution Mode
- Review Mode
- Pattern Learning Mode
- Revision Mode

---

## Solution Mode

Enter only on an explicit request (see SKILL.md, *When the user asks for the solution*). If you aren't certain of the exact problem statement, ask the user to paste it first. Then give, in this order and concisely:

1. **Intuition:** the one-sentence insight.
2. **Brute force:** the idea and its complexity, in 2–3 lines.
3. **Optimization reasoning:** what the brute force wastes, and how to stop wasting it.
4. **Pattern:** its name, plus the clue in this problem that points to it.
5. **Algorithm:** numbered plain-English steps.
5b. **Pseudocode:** language-agnostic, in a code block. It should match the algorithm line for line.
6. **Code:** in the user's language (ask once if unknown; default to Python). Clean and commented only where non-obvious.
7. **Dry run:** a variable table on one example.
8. **Complexity:** time and space, each justified.
9. **Alternatives:** other valid approaches and their trade-offs.
10. **Interview follow-ups:** 2–3 likely follow-ups (for example: "What if the input is a stream?", "Can you do it in O(1) space?").

Then:
- Log score 1 (copied) and schedule a revision for tomorrow.
- End with one task: "Close this and, in your own words, explain why the optimization works. Then tomorrow I'll ask you to rebuild it from scratch."

If the user worked through part of the problem first, acknowledge which parts they got right. The score is still based on the max hint level, so a reveal is score 1.

## Review Mode

The user submits a solution. **Don't replace it.** Review it in this order, stopping at the first serious problem:

1. **Understand their intent:** "What's your approach in one sentence?" (Skip this if it's obvious from the code or they already said it.)
2. **Correctness:** find a failing input if one exists. Give the input and ask them to trace it. Don't explain the bug yet.
3. **Edge cases:** empty, single element, duplicates, negatives, overflow, maximum size.
4. **Complexity:** ask them to state it, then confirm or challenge it.
5. **Optimization:** if a better complexity exists, say *that* it exists and what the target is ("This can be done in O(n)"). Don't say how. Offer to coach them there through workflow steps 4–6.
6. **Code quality:** naming, structure, dead code, idiomatic use of the language. Keep this brief, at most 3 points.
7. **Interview readiness:** would this pass a real interview? One line on what an interviewer would probe.

**Output format** once they've fixed any correctness bugs (or when they ask for a full review):

```markdown
**Verdict:** Correct / Incorrect / Correct but suboptimal
| Area | Status | Note |
|---|---|---|
| Correctness | ✅/❌ | ... |
| Edge cases | ✅/⚠️ | ... |
| Complexity | O(..)/O(..) | target O(..) |
| Code quality | ... | ... |
| Interview readiness | ... | ... |
**Next:** <one task>
```

**Correct solution with poor complexity:** say clearly that it's correct, which is real progress. Then: "It's O(n²). The constraints allow up to 10^5. Want to find the O(n) version yourself? I'll start with your bottleneck." Then go to workflow step 4.

## Pattern Learning Mode

The user asks to learn a pattern ("teach me sliding window"). Use [patterns.md](patterns.md). Teach interactively, **one idea per message**, and have the user answer before you move on:

1. **Intuition:** a concrete, non-code analogy or a tiny example. Then ask a question that checks it.
2. **The problem it solves:** show the brute force it replaces (for example, nested loops over subarrays) and ask the user what's wasted.
3. **Recognition signals:** the clues. Ask them to spot which of 3 short problem statements fit and which don't. Write those statements yourself, as generic descriptions, not as claimed LeetCode problems.
4. **When to use and when not:** the conditions, plus a near-miss case that breaks it.
5. **Template:** have the user fill in the blanks of a template rather than reading a finished one.
6. **Worked example:** walk through one small problem together, with the user doing the steps.
7. **Practice problem:** recommend **one** real LeetCode problem from [problem-progression.md](problem-progression.md), and offer to switch to Practice Mode for it.

For sliding window, use the deep-dive sequence in patterns.md. Do the same for other patterns: make the user discover what state to maintain, when it changes, and why that's correct.

Log the pattern as *Learning* in the pattern table (no problem score yet).

## Revision Mode

Purpose: test whether the user can **reproduce the approach without help**. Revision items come from the log's revision queue (see [progress-tracking.md](progress-tracking.md)).

1. Pick the most overdue item, or let the user choose. State only the problem number and title, and ask them to pull up the statement (or paste it).
2. **Don't show the original solution, summary, or notes.**
3. Ask, one at a time:
   - "What's the approach, from memory?"
   - "What pattern is this, and what clue tells you?"
   - "What's the complexity, and why?"
   - "What edge case tripped you up last time?" (Check this against the logged mistake, without revealing it first.)
4. Grade the recall:
   - **Pass:** approach, pattern, and complexity correct with no hints → advance the interval.
   - **Partial:** needed L1–L2 hints, or one piece was wrong → keep the same interval.
   - **Fail:** couldn't reconstruct the approach → reteach the core concept (Pattern Learning style, short), reset to a 1-day interval, and optionally have them re-solve it now.
5. **If recall is too easy** (a pass that's instant and complete), give a **variation** instead of re-solving: change one constraint and ask how the approach changes. For example: "What if the array has negatives?", "What if it's a stream?", "Return all pairs, not one", "O(1) extra space". Variations are generic twists, so describe them; don't present them as specific LeetCode problems unless you're certain.
6. If the user wants to re-code it, treat it as a normal Practice problem but start at step 6.
7. Update the log: the result, the new interval and due date, and mastery status changes.

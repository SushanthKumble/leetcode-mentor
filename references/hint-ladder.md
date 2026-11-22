# Hint Ladder

Six levels. **One level per request, never skip levels, never preview the next level.**

## Contents
- The levels
- Rules
- Making hints actually useful
- Worked example
- Tracking

## The levels

| Level | Name | What it gives | What it must NOT contain |
|---|---|---|---|
| L1 | **Nudge** | An observation the user overlooked, about the problem itself or their current attempt. | Any algorithm, pattern, or data-structure name. |
| L2 | **Direction** | What to investigate: a property, a quantity to track, a question to ask of the data. | Pattern or data-structure names. |
| L3 | **Pattern clue** | A hint toward a technique or data structure, preferably as a question. | The full algorithm or the step order. |
| L4 | **Algorithm guidance** | Help deriving the algorithm, one step or invariant at a time, through guided questions. | Pseudocode or code. |
| L5 | **Pseudocode** | Language-agnostic pseudocode of the algorithm. | Real code in the user's language. |
| L6 | **Solution** | The complete solution with full explanation (see Solution Mode in [modes.md](modes.md)). | None. |

## Rules

- **Start where they are.** The first "hint" on a problem is L1 *unless* the user is already past the stage that level addresses. For example, if they already identified the bottleneck themselves, an L1 about repeated work is useless, so start at L2. Never jump more than one level beyond what they have already worked out on their own.
- **One per request.** After giving a hint, hand control back with one question: "Does that change anything about your approach?"
- **The next request moves up one level,** unless the last hint plainly unblocked them and they're now stuck on a *different* sub-problem. In that case, restart at the lowest useful level for the new sub-problem and keep the per-problem max level for scoring.
- **"Show solution" bypasses the ladder** (see SKILL.md, *When the user asks for the solution*).
- **"Just a small hint"** means give the current level, phrased as gently as possible. It does not mean drop a level.
- **Never shame.** No "this is easy" and no "you should know this". You may say "this one trips up a lot of people".
- **No hints in Interview Mode unless asked.** When asked, the same ladder applies and the hint is recorded in the evaluation.

## Making hints actually useful

A good hint is **specific to this problem and to the user's current state**, and it changes what they'll try next. Bad hints are generic.

| ❌ Generic (don't) | ✅ Specific (do) |
|---|---|
| "Think about the constraints." | "n can be 10^5. Your nested loops do how many operations at that size?" |
| "Consider a different data structure." | "Every time you check whether you've seen a character, you rescan the substring. What if that check were instant?" |
| "Try to optimize." | "When the window hits a duplicate, you restart from `i+1`. Do the characters between the old start and the duplicate really need re-checking?" |
| "Use dynamic programming." (also a level skip) | (L2) "To know the cheapest way to reach step i, which earlier steps do you actually need?" |

Before writing any hint, ask yourself: *what does the user believe right now, and what single fact would move them forward?*

## Worked example

Problem: 3. Longest Substring Without Repeating Characters. Assume the user has a brute force that checks every substring.

- **L1 Nudge:** "In your brute force, after `'abc'` fails at the second `'a'` in `'abca'`, you start fresh from `'b'`. What do you already know about `'bc'` at that moment?"
- **L2 Direction:** "Instead of a new start for every index, think about a range `[left, right]` that's always valid. When `right` adds a duplicate, what's the smallest change to `left` that restores validity?"
- **L3 Pattern clue:** "A contiguous range that grows on the right and shrinks on the left when a condition breaks. What's that technique called, and what would you need to *store* to check for duplicates in O(1)?"
- **L4 Algorithm guidance:** "Let's build it. Step 1: `right` moves one character at a time. What should happen to your set when the new character is already in it? Walk me through `'abba'`."
- **L5 Pseudocode:**
  ```
  left = 0, best = 0, seen = empty set
  for right in 0..n-1:
      while s[right] in seen:
          remove s[left] from seen; left += 1
      add s[right] to seen
      best = max(best, right - left + 1)
  return best
  ```
- **L6 Solution:** full code in the user's language, plus intuition, dry run, complexity, and variants (last-index map to jump `left` directly).

## Tracking

For each problem, record the **highest level reached** (L0 = none) and whether a solution was revealed. This determines the independence score in [progress-tracking.md](progress-tracking.md):

| Max hint level | Independence | Score |
|---|---|---|
| none | Independent | 5 |
| L1–L2 | Minor hints | 4 |
| L3–L4 | Major hints | 3 |
| L5, or approach explained before the user coded it | After seeing the approach | 2 |
| L6 / full solution | Copied solution | 1 |

Clarifying the *problem statement* (not the solution) is not a hint and doesn't count. Neither is correcting a factual misunderstanding of the problem. Correcting a user's *code bug* by pointing at a failing input counts as L1 only if the user couldn't find the bug after their own dry run.

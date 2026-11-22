# Progress Tracking

A single, human-readable Markdown file: `leetcode-log.md` in the user's current working directory. It's simple and transparent, and the user can edit it.

## Contents
- Ground rules
- Log file format
- Independence scores
- Mastery status
- Spaced repetition
- Difficulty progression
- Returning after a break

## Ground rules

- **Ask before creating the file** the first time (see SKILL.md). If the user declines, or there's no file system, keep everything in the conversation only.
- **Never fabricate.** Only record what happened in a session. If the log and your memory disagree, the log wins. If an entry is ambiguous, ask.
- **Write at milestones,** not every message: when a problem is finished or abandoned, after a revision, after an interview, after a pattern lesson, and when the user stops mid-problem (save the *Active problem* section).
- **Edit in place.** Use your file-editing tools to update the relevant sections. Don't rewrite the whole file unnecessarily, and don't delete history.
- **Use dates in ISO format** (YYYY-MM-DD). Get today's date from the environment. If it's unknown, ask the user once.
- **No personal data** beyond what the user volunteers about their practice (for example, preferred language). This file belongs to the user, and it's excluded from the skill's repository by `.gitignore`.

## Log file format

Create it with this skeleton, filling in only what's known:

```markdown
# LeetCode Practice Log
_Maintained by the leetcode-mentor skill. You can edit this file; the mentor treats your edits as the truth._

## Profile
- Language: <e.g. Python>
- Current focus: <Easy | Medium | Hard> fundamentals
- Last session: YYYY-MM-DD

## Daily problem
<!-- one line per day, written by scripts/mentor.py:
- YYYY-MM-DD: N. Title (Difficulty) · status: pending|done|skipped · why: <reason, never the pattern>
-->

## Active problem
_None._
<!-- or:
- Problem: 322. Coin Change (Medium)
- Reached: Step 3 (brute force recursion, correct, O(k^n))
- Max hint level so far: L1
- Notes: user believes greedy works; disproved with coins [1,3,4], amount 6
-->

## Revision queue
| Due | Problem | Pattern | Interval (days) | Last result |
|---|---|---|---|---|

## Pattern mastery
| Pattern | Problems | Best score | Status | Recognition clue (user's words) | Confused with |
|---|---|---|---|---|---|

## Mistake patterns
<!-- recurring mistakes, with counts, e.g.:
- Off-by-one when shrinking a window (2×)
- Claims O(n) for nested loops without amortized argument (1×)
-->

## Problem history
<!-- newest first, one block per attempt -->
```

**Problem history entry** (written at step 10, or on abandon or reveal):

```markdown
### YYYY-MM-DD: 3. Longest Substring Without Repeating Characters (Medium)
- **Outcome:** Minor hints (score 4) · max hint L2 · solution revealed: no
- **Pattern:** Sliding window (variable size)
- **Key observation:** When a duplicate enters, only the left boundary must move; never restart.
- **Brute force:** check all substrings, O(n³) → O(n²) with a set
- **Optimized:** window + set/last-index map, O(n) time, O(min(n, alphabet)) space
- **Pseudocode:**
  ```
  left = 0; best = 0; seen = {}
  for right in 0..n-1:
      while s[right] in seen: remove s[left]; left++
      add s[right]; best = max(best, right-left+1)
  return best
  ```
- **Mistakes:** moved `left` to `i+1` instead of past the duplicate
- **Complexity misunderstanding:** thought the inner while made it O(n²); fixed with the amortized argument
- **Takeaway (user's words):** "..."
- **Mastered:** no (needs an independent revision)
```

## Independence scores

| Score | Level | Meaning |
|---|---|---|
| 5 | **Independent** | No hints. Problem-statement clarification is OK. |
| 4 | **Minor hints** | Max hint L1–L2 |
| 3 | **Major hints** | Max hint L3–L4 |
| 2 | **After seeing the approach** | L5 pseudocode, or the approach was explained before they coded it |
| 1 | **Copied solution** | L6 or the full solution revealed |
| 0 | **Abandoned** | Stopped without solving; resume later |

A user who asks for the solution and then codes it themselves is still score 1 for that attempt. They can raise it on a later revision.

## Mastery status

**Problem:**
- *Attempted* → *Solved* (any score ≥ 1 with a working solution) → **Mastered**, when all of these hold:
  1. at least one attempt or revision at score 5 (independent),
  2. the takeaway stated in the user's own words, and
  3. a passed revision at an interval of ≥ 7 days.
- Reading a solution never makes a problem Mastered.

**Pattern:**
| Status | Rule |
|---|---|
| New | Never practiced |
| Learning | Taught (Pattern Learning Mode) or only scores ≤ 3 |
| Practicing | ≥ 1 problem at score ≥ 4 |
| Solid | ≥ 3 *distinct* problems at score ≥ 4, at least 2 of them at 5 |
| Mastered | Solid, plus it was recognized independently in a **mixed** (unlabeled) problem or an interview, plus a passed 14+ day revision |

Recognizing a pattern only when the problem was labeled with it (for example, from a "sliding window" list) counts less. Note in the entry whether the problem was labeled.

## Spaced repetition

Intervals: **1 → 3 → 7 → 14 → 30 days**, then retire the item.

**First interval after an attempt**, based on its score:
| Score | Next review |
|---|---|
| 0–2 | 1 day |
| 3 | 3 days |
| 4 | 7 days |
| 5 | 14 days |

**After a revision** (see Revision Mode in [modes.md](modes.md)):
- **Pass** → the next interval up the ladder. Passing at 30 retires the item and, if the mastery criteria are met, marks the problem Mastered.
- **Partial** → repeat the same interval.
- **Fail** → back to 1 day, reteach the concept, and add the cause to *Mistake patterns*.

**Due items** are those with a due date ≤ today. At session start, mention the count. In Revision Mode, take the most overdue first. Don't force revisions; the user chooses.

## Difficulty progression

Decide **per pattern**, from consistency and independence, never from a single solve:

- **Easy → Medium** for a pattern: the last 3 problems with that pattern scored ≥ 4, and at least 2 of them were 5.
- **Medium → Hard:** the pattern is *Solid* and the user has solved at least 2 mixed Medium problems independently.
- **Step back** a level: two consecutive scores ≤ 2 at the current level for that pattern.
- *Current focus* in the Profile is the level where most of the user's foundational patterns sit.

## Returning after a break

When the user comes back after several days:
1. Read the log. Summarize in **at most 3 lines**: the last session date, any active problem, the number of revisions due, and the weakest pattern.
2. Offer **one** recommended action, with the reason. Usually: "You have 3 revisions due. Start with *Coin Change*, which you needed major hints on." Or: "Resume *Coin Change* where you left off."
3. If it's been more than 2 weeks, suggest a revision before new problems.
4. If no log exists, say so honestly ("I don't have any saved progress here"), and start fresh. Never pretend to remember.

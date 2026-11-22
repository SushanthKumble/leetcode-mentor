# LeetCode Practice Log
_Demo data for screenshots. Not a real user._

## Profile
- Language: Python
- LeetCode username: (not set)
- Goal: coding interviews in about 3 months
- Target date: 2027-02-26
- Daily time: 45 min
- Days per week: 6
- Previous solves: placement
- Start stage: 1
- Current focus: Medium fundamentals
- Onboarding: done (2026-11-06)
- Last session: 2026-11-22

## Study plan

- Created: 2026-11-06 · Pace: 1 new problem a day, 6 days a week (~45 min a day)
- Goal: coding interviews in about 3 months · Target date: 2027-02-26
- Starting point: Stage 1 · Previous solves: placement check (0 past solves skipped)
- Roadmap:
  - Stage 1 · Foundations (arrays, hashing, strings): 8 problems · 2026-11-06 → 2026-11-15
  - Stage 2 · Linear techniques: 20 problems · 2026-11-16 → 2026-12-09
  - Stage 3 · Linked lists and trees: 19 problems · 2026-12-10 → 2027-01-01
  - Stage 4 · Heaps, intervals, greedy, backtracking: 21 problems · 2027-01-02 → 2027-01-26
  - Stage 5 · Graphs, DP, advanced structures: 28 problems · 2027-01-27 → 2027-02-28
- Daily: revisions due first (10–15 min), then today's problem
- Weekly: one mock interview from Stage 3 (around 2026-12-10)
- Target check: tight. At this pace you finish Stage 4 by the target date. Options: add a 2nd problem on some days, practice more days a week, or focus on Stages 1–3.

## Daily problem

- 2026-11-21: 20. Valid Parentheses (Easy) · status: done · why: Builds on a topic where you've needed hints.
- 2026-11-22: 739. Daily Temperatures (Medium) · status: done · why: A new topic for you. The mentor will check the basics before you start.

## Active problem
_None._

## Revision queue
| Due | Problem | Pattern | Interval (days) | Last result |
|---|---|---|---|---|
| 2026-11-21 | 238. Product of Array Except Self | Prefix products | 1 | Saw approach (score 2) |
| 2026-11-23 | 424. Longest Repeating Character Replacement | Sliding window | 3 | Major hints (score 3) |
| 2026-11-26 | 15. 3Sum | Two pointers | 3 | Major hints (score 3) |
| 2026-11-29 | 739. Daily Temperatures | Monotonic stack | 7 | Minor hints (score 4) |
| 2026-12-06 | 1. Two Sum | Hashing | 30 | Revision passed |

## Pattern mastery
| Pattern | Problems | Best score | Status | Recognition clue (user's words) | Confused with |
|---|---|---|---|---|---|
| Hashing | 4 | 5 | Solid | "need to know if I've seen it, fast" | |
| Two pointers | 3 | 5 | Practicing | "sorted + pair" | sliding window |
| Sliding window | 3 | 5 | Practicing | "contiguous + longest/shortest" | two pointers |

## Mistake patterns
- Off-by-one when shrinking a window (2x)
- Forgets to skip duplicates after sorting (1x)
- Claims O(n^2) for amortized while-inside-for (1x)

## Problem history
### 2026-11-22: 739. Daily Temperatures (Medium)
- **Outcome:** Minor hints (score 4) · max hint L2 · solution revealed: no
- **Pattern:** Monotonic stack
- **Pseudocode:**
  ```
  ans = [0]*n; stack = []
  for i in 0..n-1:
      while stack and t[stack.top] < t[i]:
          j = stack.pop(); ans[j] = i - j
      stack.push(i)
  return ans
  ```
- **Takeaway (user's words):** "keep unresolved days on a stack; a warmer day resolves them"
- **Mastered:** no

### 2026-11-21: 20. Valid Parentheses (Easy)
- **Outcome:** Independent (score 5) · max hint none · solution revealed: no
- **Pattern:** Stack
- **Takeaway (user's words):** "the most recent opener must close first"
- **Mastered:** no

### 2026-11-20: 424. Longest Repeating Character Replacement (Medium)
- **Outcome:** Major hints (score 3) · max hint L3 · solution revealed: no
- **Pattern:** Sliding window
- **Takeaway (user's words):** "window is valid while length - maxFreq <= k"
- **Mastered:** no

### 2026-11-19: 3. Longest Substring Without Repeating Characters (Medium)
- **Outcome:** Minor hints (score 4) · max hint L1 · solution revealed: no
- **Pattern:** Sliding window
- **Pseudocode:**
  ```
  left = 0; best = 0; seen = {}
  for right in 0..n-1:
      while s[right] in seen: remove s[left]; left++
      add s[right]; best = max(best, right-left+1)
  return best
  ```
- **Takeaway (user's words):** "never restart; move left past the duplicate"
- **Mastered:** no

### 2026-11-18: 121. Best Time to Buy and Sell Stock (Easy)
- **Outcome:** Independent (score 5) · max hint none · solution revealed: no
- **Pattern:** Sliding window
- **Takeaway (user's words):** "track the cheapest price so far"
- **Mastered:** no

### 2026-11-16: 15. 3Sum (Medium)
- **Outcome:** Major hints (score 3) · max hint L4 · solution revealed: no
- **Pattern:** Two pointers
- **Takeaway (user's words):** "sort, fix one, two-pointer the rest, skip duplicates"
- **Mastered:** no

### 2026-11-15: 167. Two Sum II - Input Array Is Sorted (Medium)
- **Outcome:** Independent (score 5) · max hint none · solution revealed: no
- **Pattern:** Two pointers
- **Takeaway (user's words):** "sorted input: move the pointer that fixes the sum"
- **Mastered:** no

### 2026-11-14: 125. Valid Palindrome (Easy)
- **Outcome:** Independent (score 5) · max hint none · solution revealed: no
- **Pattern:** Two pointers
- **Takeaway (user's words):** "compare from both ends, skip non-alphanumerics"
- **Mastered:** no

### 2026-11-13: 238. Product of Array Except Self (Medium)
- **Outcome:** Saw approach (score 2) · max hint L5 · solution revealed: no
- **Pattern:** Prefix products
- **Takeaway (user's words):** "prefix product times suffix product"
- **Mastered:** no

### 2026-11-12: 724. Find Pivot Index (Easy)
- **Outcome:** Minor hints (score 4) · max hint L1 · solution revealed: no
- **Pattern:** Prefix sums
- **Takeaway (user's words):** "left sum equals total minus left minus current"
- **Mastered:** no

### 2026-11-10: 49. Group Anagrams (Medium)
- **Outcome:** Independent (score 5) · max hint none · solution revealed: no
- **Pattern:** Hashing
- **Takeaway (user's words):** "sorted word (or counts) as the group key"
- **Mastered:** no

### 2026-11-09: 242. Valid Anagram (Easy)
- **Outcome:** Independent (score 5) · max hint none · solution revealed: no
- **Pattern:** Hashing
- **Takeaway (user's words):** "equal character counts"
- **Mastered:** yes

### 2026-11-08: 217. Contains Duplicate (Easy)
- **Outcome:** Independent (score 5) · max hint none · solution revealed: no
- **Pattern:** Hashing
- **Takeaway (user's words):** "a set answers have-I-seen-it in O(1)"
- **Mastered:** yes

### 2026-11-07: 1. Two Sum (Easy)
- **Outcome:** Independent (score 5) · max hint none · solution revealed: no
- **Pattern:** Hashing
- **Takeaway (user's words):** "store what I've seen, look up the complement"
- **Mastered:** yes

# Problem Progression and Selection

## Contents
- Selection rules
- How to present a recommendation
- Curated ladder (by stage)
- "Random problem" requests

## Selection rules

Recommend **one problem at a time**. Choose it this way:

1. **Due revisions come first.** If any are due, offer the most overdue one *or* a new problem, and let the user pick.
2. **Resume the active problem** if there is one, unless the user wants something new.
3. **Choose the stage.** Use the earliest stage in the ladder below that still has a pattern below *Practicing*. Foundations come before advanced topics.
4. **Within the stage,** pick the weakest pattern, preferring those with a recent fail or a score ≤ 3.
5. **Match the difficulty** to the pattern's level (see [progress-tracking.md](progress-tracking.md), Difficulty progression).
6. **Avoid monotony.** Don't give the same pattern more than **2 problems in a row** unless the user asked to drill it.
7. **Mix in unlabeled problems.** Roughly every 4th problem, choose from an earlier stage or a different pattern, *without naming the pattern*. This trains recognition, the skill interviews actually test.
8. **Never repeat** a problem from the history unless it's a revision.
9. **Only recommend problems listed here,** or ones you are certain exist with that exact number and title. If you are unsure of a title, number, or statement, don't guess. Ask the user to paste the problem, or choose one from this list.

With no log (a new user), start at Stage 1, Easy, and ask one calibration question first: "Roughly how many LeetCode problems have you solved, and which topics feel comfortable?"

## How to present a recommendation

Keep it short, and **don't reveal the pattern for mixed or unlabeled picks**, because that would spoil the recognition step.

> **Next: 739. Daily Temperatures (Medium)**
> Why: you've solved a few array problems with minor hints. This one tests whether you can spot an optimization on your own. Open it on LeetCode (or paste the statement here), and tell me in your own words what it asks.

For an explicit drill ("give me a sliding window problem"), naming the pattern is fine.

## Curated ladder

Every problem below is a real, free LeetCode problem (number, title, difficulty and URL slug checked against LeetCode on 2026-11-22), listed by number and title. Difficulty is shown as E/M/H. The patterns are for **your selection logic only**.

### Stage 1: Foundations (arrays, hashing, strings)
| Pattern | Problems |
|---|---|
| Hashing | 1. Two Sum (E) · 217. Contains Duplicate (E) · 242. Valid Anagram (E) · 49. Group Anagrams (M) · 347. Top K Frequent Elements (M) · 128. Longest Consecutive Sequence (M) |
| Arrays / prefix | 724. Find Pivot Index (E) · 303. Range Sum Query - Immutable (E) · 238. Product of Array Except Self (M) · 560. Subarray Sum Equals K (M) |
| Two pointers | 125. Valid Palindrome (E) · 283. Move Zeroes (E) · 977. Squares of a Sorted Array (E) · 167. Two Sum II - Input Array Is Sorted (M) · 15. 3Sum (M) · 11. Container With Most Water (M) · 42. Trapping Rain Water (H) |

### Stage 2: Linear techniques
| Pattern | Problems |
|---|---|
| Sliding window | 643. Maximum Average Subarray I (E) · 121. Best Time to Buy and Sell Stock (E) · 3. Longest Substring Without Repeating Characters (M) · 424. Longest Repeating Character Replacement (M) · 567. Permutation in String (M) · 1004. Max Consecutive Ones III (M) · 76. Minimum Window Substring (H) |
| Stack | 20. Valid Parentheses (E) · 232. Implement Queue using Stacks (E) · 155. Min Stack (M) · 150. Evaluate Reverse Polish Notation (M) · 22. Generate Parentheses (M) |
| Monotonic stack / deque | 496. Next Greater Element I (E) · 739. Daily Temperatures (M) · 853. Car Fleet (M) · 84. Largest Rectangle in Histogram (H) · 239. Sliding Window Maximum (H) |
| Binary search | 704. Binary Search (E) · 35. Search Insert Position (E) · 278. First Bad Version (E) · 74. Search a 2D Matrix (M) · 875. Koko Eating Bananas (M) · 153. Find Minimum in Rotated Sorted Array (M) · 33. Search in Rotated Sorted Array (M) · 4. Median of Two Sorted Arrays (H) |

### Stage 3: Linked lists and trees
| Pattern | Problems |
|---|---|
| Linked list / fast-slow | 206. Reverse Linked List (E) · 21. Merge Two Sorted Lists (E) · 876. Middle of the Linked List (E) · 141. Linked List Cycle (E) · 202. Happy Number (E) · 142. Linked List Cycle II (M) · 287. Find the Duplicate Number (M) |
| Tree DFS | 226. Invert Binary Tree (E) · 104. Maximum Depth of Binary Tree (E) · 100. Same Tree (E) · 543. Diameter of Binary Tree (E) · 110. Balanced Binary Tree (E) · 572. Subtree of Another Tree (E) · 235. Lowest Common Ancestor of a Binary Search Tree (M) · 98. Validate Binary Search Tree (M) · 230. Kth Smallest Element in a BST (M) · 124. Binary Tree Maximum Path Sum (H) |
| Tree BFS | 102. Binary Tree Level Order Traversal (M) · 199. Binary Tree Right Side View (M) |

### Stage 4: Heaps, intervals, greedy, backtracking
| Pattern | Problems |
|---|---|
| Heap | 703. Kth Largest Element in a Stream (E) · 1046. Last Stone Weight (E) · 215. Kth Largest Element in an Array (M) · 973. K Closest Points to Origin (M) · 621. Task Scheduler (M) · 23. Merge k Sorted Lists (H) · 295. Find Median from Data Stream (H) |
| Intervals | 56. Merge Intervals (M) · 57. Insert Interval (M) · 435. Non-overlapping Intervals (M) |
| Greedy | 53. Maximum Subarray (M) · 55. Jump Game (M) · 45. Jump Game II (M) · 134. Gas Station (M) · 763. Partition Labels (M) |
| Backtracking | 78. Subsets (M) · 39. Combination Sum (M) · 46. Permutations (M) · 17. Letter Combinations of a Phone Number (M) · 79. Word Search (M) · 51. N-Queens (H) |

### Stage 5: Graphs, DP, advanced structures
| Pattern | Problems |
|---|---|
| Graph DFS/BFS | 1971. Find if Path Exists in Graph (E) · 200. Number of Islands (M) · 695. Max Area of Island (M) · 133. Clone Graph (M) · 994. Rotting Oranges (M) · 207. Course Schedule (M) · 210. Course Schedule II (M) · 127. Word Ladder (H) |
| Union-find | 547. Number of Provinces (M) · 684. Redundant Connection (M) |
| 1-D DP | 70. Climbing Stairs (E) · 746. Min Cost Climbing Stairs (E) · 198. House Robber (M) · 213. House Robber II (M) · 322. Coin Change (M) · 300. Longest Increasing Subsequence (M) · 416. Partition Equal Subset Sum (M) |
| 2-D DP | 62. Unique Paths (M) · 1143. Longest Common Subsequence (M) · 72. Edit Distance (M) |
| Trie | 208. Implement Trie (Prefix Tree) (M) · 211. Design Add and Search Words Data Structure (M) · 212. Word Search II (H) |
| Bit manipulation | 136. Single Number (E) · 191. Number of 1 Bits (E) · 338. Counting Bits (E) · 268. Missing Number (E) · 190. Reverse Bits (E) |

LeetCode occasionally re-labels a problem's difficulty or edits its statement. Treat the difficulty labels as approximate, and always work from the statement the user sees.

## "Random problem" requests

"Random" means **unpredictable to the user**, not uniformly random. Pick an unlabeled problem using the selection rules, one stage at or below the user's current focus, and don't name the pattern. If there's no log, choose a Stage 1–2 Easy or Medium problem and ask the calibration question afterward if useful.

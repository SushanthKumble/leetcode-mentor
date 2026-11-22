# Pattern Reference

Use this **after** the user has a brute force and has found the bottleneck. The goal is *transfer*: the user should learn to recognize the clue, not memorize "problem X uses Y".

For each pattern, these are the six things the user should be able to say: **Clues** · **Applies when** · **Why it works** · **Template** · **Fails when** · **Alternatives / confusables**.

## Contents
1. Hashing
2. Two pointers
3. Sliding window (with deep-dive teaching guide)
4. Fast and slow pointers
5. Prefix sums
6. Binary search (on index and on answer)
7. Sorting
8. Intervals
9. Stack
10. Monotonic stack / deque
11. Queue
12. Heap / priority queue
13. Tree DFS
14. Tree BFS
15. Graph DFS
16. Graph BFS
17. Backtracking
18. Greedy
19. Dynamic programming
20. Union-find
21. Trie
22. Bit manipulation
- Bottleneck → candidate pattern map
- Constraint → target complexity

---

## 1. Hashing
- **Clues:** "have I seen X before?", counting frequencies, finding a complement, grouping by a key, duplicates.
- **Applies when:** you repeatedly search for an exact value or key, and order doesn't matter.
- **Why it works:** it trades O(n) space for O(1) average lookup, so the repeated linear search disappears.
- **Template:** `seen = {}; for x in items: if need(x) in seen: answer; seen[key(x)] = info`
- **Fails when:** you need order or range queries ("smallest greater than x"), or memory is tightly bounded.
- **Alternatives:** sort plus two pointers (O(1) extra space, O(n log n)); a counting array when values are small; a balanced BST or sorted container when you need order.

## 2. Two pointers
- **Clues:** sorted input, pairs or triplets meeting a target, palindromes, in-place partition or dedupe, merging two sorted lists.
- **Applies when:** moving one pointer has a *monotonic* effect, so you can always tell which pointer to move without missing an answer.
- **Why it works:** each move eliminates a whole row or column of candidate pairs, which turns O(n²) into O(n).
- **Template:** `l, r = 0, n-1; while l < r: if f(l,r) too small: l++ elif too big: r-- else record; move both`
- **Fails when:** the input is unsorted and sorting destroys needed information (for example, original indices), or moving a pointer has no monotonic effect.
- **Alternatives:** hashing (unsorted input), binary search for the partner (O(n log n)).

## 3. Sliding window
- **Clues:** *contiguous* subarray or substring; longest, shortest, or count of windows satisfying a condition; "at most K", "exactly K" (= atMost(K) − atMost(K−1)).
- **Applies when:** validity is monotonic in window size. If a window is valid, shrinking it keeps it valid (or growing keeps it invalid), so neither boundary ever needs to move backward.
- **Why it works:** each element enters and leaves the window at most once, so the total work is O(n) even though there is a nested `while`.
- **Template (variable size):**
  ```
  left = 0; state = empty
  for right in range(n):
      add a[right] to state
      while window invalid: remove a[left] from state; left += 1
      update answer with window [left, right]
  ```
  **Fixed size k:** add `a[right]`, remove `a[right-k]` once `right ≥ k`, then update.
- **Fails when:** the condition isn't monotonic. For example, with negative numbers in "subarray sum = K", shrinking can increase the sum. Use prefix sums plus hashing instead.
- **Alternatives:** prefix sums plus hashing (negatives, exact sums); two pointers (non-contiguous pairs); a monotonic deque (max or min of each window).

### Sliding-window deep dive (how to teach it)
Guide the user through these, one question each, using their own brute force:
1. **Why are nested loops wasteful?** "When the window `[i, j]` becomes invalid, your brute force restarts at `i+1` and rebuilds everything. What part of that rebuilding was already known?"
2. **What does the window maintain?** A count map, a sum, a set, or the number of distinct items. "What's the smallest state that lets you check validity in O(1)?"
3. **When does it expand or shrink?** It always expands on the right. It shrinks on the left *while* invalid (for the longest valid window) or *while* valid (for the shortest valid window).
4. **What makes it valid?** Have the user write the condition as code: `len(set) == window size`, `sum ≥ target`, `window_len − max_freq ≤ k`.
5. **Fixed or variable?** Is the size given (k) or the thing being optimized?
6. **Break it:** "What if the array had negative numbers?" This is how they learn the boundary of the pattern.

## 4. Fast and slow pointers
- **Clues:** linked-list cycle, the middle of a list, the k-th from the end, a "happy number"-style repeated function, duplicate detection with O(1) space in values 1..n.
- **Applies when:** you traverse a sequence defined by `next(x)` that may eventually repeat.
- **Why it works:** in a cycle, the speed difference closes the gap by 1 each step, so they must meet. Distance arithmetic then locates the cycle start.
- **Template:** `slow = fast = head; while fast and fast.next: slow = slow.next; fast = fast.next.next; if slow is fast: cycle`
- **Fails when:** random access is available and O(n) space is fine, so a hash set is simpler.
- **Alternatives:** a hash set of visited nodes (O(n) space).

## 5. Prefix sums
- **Clues:** many range-sum queries; "subarray sum equals K" (with negatives); balance and equilibrium points; 2D region sums.
- **Applies when:** the operation is invertible (sum, XOR, count), so `range(i, j) = P[j+1] − P[i]`.
- **Why it works:** precomputing cumulative values turns each range query into O(1). Pairing it with a hash map of past prefixes finds the target range in one pass.
- **Template:** `count = {0:1}; s = 0; for x in a: s += x; ans += count.get(s-k, 0); count[s] += 1`
- **Fails when:** the operation isn't invertible (min or max). Use a sparse table or segment tree. It also fails when the array is updated often (use a Fenwick or segment tree).
- **Alternatives:** sliding window (all non-negative values), difference arrays (range updates).

## 6. Binary search
- **Clues:** sorted data; "find the first or last position where…"; O(log n) required; **"minimum maximum" / "smallest k such that…"** (binary search on the answer).
- **Applies when:** there's a **monotonic predicate**: false…false true…true over the index or answer space.
- **Why it works:** each comparison discards half the candidates, and monotonicity guarantees the answer isn't in the discarded half.
- **Template:** `lo, hi = low, high; while lo < hi: mid = (lo+hi)//2; if ok(mid): hi = mid else: lo = mid+1; return lo`
- **Fails when:** the predicate isn't monotonic. Off-by-one errors come from mixing interval conventions, so have the user state their invariant (`[lo, hi)` or `[lo, hi]`).
- **Alternatives:** a linear scan (small n), two pointers, a heap.

## 7. Sorting
- **Clues:** order doesn't matter in the output; pairing or grouping neighbors; intervals; "k-th"; greedy choices that need order.
- **Applies when:** you can afford O(n log n) and either the original order isn't needed or you can carry indices along.
- **Why it works:** it creates structure (adjacency of equal or near values, monotonic order) that enables two pointers, greedy, or binary search.
- **Template:** `items.sort(key=...)`, then scan.
- **Fails when:** an O(n) solution is required, or original positions matter.
- **Alternatives:** hashing, counting or bucket sort (bounded values), a heap (only the top k needed).

## 8. Intervals
- **Clues:** start/end pairs, meetings, overlapping ranges, merge, insert, minimum rooms, removing overlaps.
- **Applies when:** sorting by start (merge) or by end (greedy selection) makes overlap a local, adjacent check.
- **Why it works:** after sorting, an interval can only overlap the current merged block or later ones, never an earlier finished one.
- **Template:** `sort by start; for s,e: if s <= last_end: last_end = max(last_end, e) else: push new`
- **Fails when:** the question needs point queries over many intervals (use a sweep line, segment tree, or heap of end times).
- **Alternatives:** sweep line (+1/−1 events), a min-heap of end times (room counting).

## 9. Stack
- **Clues:** matching or nesting (parentheses, tags), "most recent unmatched", undo, expression evaluation, simulating recursion.
- **Applies when:** the next item to resolve is always the most recently opened one (LIFO).
- **Why it works:** a stack keeps exactly the unresolved items in the order they must be resolved.
- **Template:** `for t in tokens: if opens: push; else: check/pop top`
- **Fails when:** resolution order is first-in-first-out (use a queue) or depends on priority (use a heap).
- **Alternatives:** a counter (single bracket type), recursion.

## 10. Monotonic stack / deque
- **Clues:** "next greater or smaller element", "days until warmer", spans, the largest rectangle in a histogram, the max or min of each sliding window.
- **Applies when:** each element only needs its nearest greater or smaller neighbor, and elements dominated by a newer one can never be an answer again.
- **Why it works:** you pop dominated elements the moment they're resolved. Each element is pushed and popped once, so it's O(n) amortized.
- **Template:** `for i, x: while stack and a[stack[-1]] < x: j = pop(); answer[j] = i; push(i)`
- **Fails when:** you need arbitrary range queries rather than nearest-neighbor ones.
- **Alternatives:** a brute-force scan (O(n²)), a segment tree, a heap (window max with lazy deletion, O(n log n)).

## 11. Queue
- **Clues:** process in arrival order, level by level, streaming, a recent-window counter, BFS.
- **Applies when:** first-in-first-out order is required.
- **Why it works:** it preserves arrival or discovery order, which is what makes BFS find shortest paths in unweighted graphs.
- **Template:** `q = deque([start]); while q: x = q.popleft(); for y in next(x): q.append(y)`
- **Fails when:** priority matters more than arrival (use a heap).
- **Alternatives:** a deque (both ends), a circular buffer.

## 12. Heap / priority queue
- **Clues:** "k largest or smallest", "k closest", merge k sorted lists, a running median, schedule by earliest or cheapest, Dijkstra.
- **Applies when:** you repeatedly need the current min or max while items are inserted.
- **Why it works:** O(log n) insert and pop-min. Keeping a heap of size k gives O(n log k).
- **Template (top-k largest):** `h = []; for x: push(h, x); if len(h) > k: pop(h)` → `h` holds the k largest.
- **Fails when:** you need arbitrary deletion or ordered iteration (use a sorted container), or one pass with quickselect suffices.
- **Alternatives:** sorting (O(n log n)), quickselect (O(n) average), bucket sort (bounded frequencies).

## 13. Tree DFS
- **Clues:** depth, height, diameter, path sums, validate a BST, lowest common ancestor, serialize, "for every node, compute from its children".
- **Applies when:** a node's answer depends on its subtrees' answers (post-order) or on information from its ancestors (pre-order, passed as parameters).
- **Why it works:** recursion mirrors the tree's recursive definition. Each node is visited once.
- **Template:** `def dfs(node): if not node: return base; L = dfs(node.left); R = dfs(node.right); update global with L,R; return combine(L,R,node)`
- **Fails when:** the tree is very deep and recursion overflows (use an iterative stack), or the question is about levels (use BFS).
- **Alternatives:** BFS, iterative DFS, Morris traversal (O(1) space).
- **Teach:** "What does dfs *return*, and what does it *record globally*?" The diameter and max path sum problems hinge on that difference.

## 14. Tree BFS
- **Clues:** level order, right-side view, the minimum depth, zigzag, connecting next pointers, "closest to the root".
- **Applies when:** the answer is organized by depth.
- **Why it works:** a queue processes all nodes at depth d before depth d+1. Snapshot `len(q)` to separate levels.
- **Template:** `while q: for _ in range(len(q)): node = q.popleft(); ...; push children`
- **Fails when:** the answer needs subtree aggregation (DFS is more natural).
- **Alternatives:** DFS carrying the depth as a parameter.

## 15. Graph DFS
- **Clues:** connected components, islands, cycle detection, topological order, "can I reach", path existence, flood fill.
- **Applies when:** you need to fully explore reachability. Order of discovery doesn't need to be by distance.
- **Why it works:** a visited set guarantees each vertex and edge is processed once, giving O(V + E).
- **Template:** `def dfs(u): visited.add(u); for v in adj[u]: if v not in visited: dfs(v)`. For directed cycles, track three colors: unvisited, in-stack, done.
- **Fails when:** shortest paths are needed (use BFS or Dijkstra), or recursion depth is an issue on large grids.
- **Alternatives:** BFS, union-find (connectivity only), Kahn's algorithm (topological sort).

## 16. Graph BFS
- **Clues:** **shortest path in an unweighted graph or grid**, minimum steps or moves, "nearest", word ladder, multi-source spread (rotting oranges).
- **Applies when:** every edge has equal cost.
- **Why it works:** nodes are dequeued in non-decreasing distance order, so the first visit is the shortest.
- **Template:** `q = deque(sources); dist[s] = 0; while q: u = q.popleft(); for v in adj[u]: if v unseen: dist[v] = dist[u]+1; q.append(v)`. Mark nodes when *enqueuing*, not when dequeuing.
- **Fails when:** edges have different weights (use Dijkstra), or with 0/1 weights (use 0-1 BFS with a deque).
- **Alternatives:** DFS (reachability only), Dijkstra, bidirectional BFS.

## 17. Backtracking
- **Clues:** "all" or "every" combination, permutation, subset, partition, placement (N-Queens), small n (≤ ~20), word search in a grid.
- **Applies when:** you must enumerate or search a space of choices, and partial choices can be checked or pruned.
- **Why it works:** it builds candidates incrementally and abandons a branch as soon as it can't lead to a valid answer.
- **Template:** `def bt(state, choices): if complete: record; return; for c in choices: if valid(c): apply(c); bt(...); undo(c)`
- **Fails when:** only a count or an optimum is needed and subproblems overlap (use DP), or the input is too large for exponential time.
- **Alternatives:** DP (counting or optimizing), bitmask enumeration.
- **Teach:** "What's the choice at each step, what's the undo, and how do you avoid duplicates?" (Sort, then skip equal siblings.)

## 18. Greedy
- **Clues:** "minimum number of…", "maximum number of non-overlapping…", jump games, gas station, scheduling, partition labels.
- **Applies when:** a locally optimal choice can be **proved** never to hurt, through an exchange argument or a "stays ahead" argument.
- **Why it works:** the proof shows any optimal solution can be transformed to include the greedy choice.
- **Template:** sort or scan by the key that the proof relies on, take the best safe choice, and never revisit it.
- **Fails when:** an earlier choice can block a better later one, for example coin change with arbitrary denominations. **Always ask the user for a counterexample attempt before accepting a greedy approach.**
- **Alternatives:** DP (when greedy is unprovable or false), a heap-based greedy.

## 19. Dynamic programming
- **Clues:** count the ways, min or max cost, "can you reach or partition", choices at each step whose results depend on earlier choices, and a brute-force recursion that recomputes the same arguments.
- **Applies when:** there are **overlapping subproblems** and **optimal substructure**.
- **Why it works:** each distinct subproblem is solved once and stored, so time is (number of states) × (work per state).
- **Template:** define the state in words → recurrence → base cases → evaluation order (memoized recursion or a bottom-up table) → the answer's location → space optimization.
- **Fails when:** subproblems don't overlap (plain recursion or divide and conquer is enough), or the state space is too large.
- **Alternatives:** greedy (if provable), BFS (shortest steps), backtracking (when all solutions must be listed).
- **Teach:** start from the user's brute-force recursion. "Which arguments repeat? Draw the call tree for n = 5." Memoization is then their own idea.

## 20. Union-find (disjoint set union)
- **Clues:** dynamic connectivity, "are these in the same group", merging accounts, a redundant edge, the number of components as edges arrive.
- **Applies when:** you only need connectivity (not paths), and edges are only added.
- **Why it works:** with path compression and union by rank, each operation is nearly O(1) amortized (inverse Ackermann).
- **Template:** `find(x): if parent[x] != x: parent[x] = find(parent[x]); return parent[x]`; `union(a,b): ra, rb = find(a), find(b); if ra == rb: return False; attach smaller rank under larger`
- **Fails when:** you need actual paths or distances, or edges are deleted.
- **Alternatives:** DFS or BFS (static graph), topological sort (directed graphs).

## 21. Trie
- **Clues:** prefix queries, autocomplete, "starts with", a word dictionary with wildcards, searching many words in a grid.
- **Applies when:** many strings share prefixes and you query by prefix.
- **Why it works:** shared prefixes are stored once, and a lookup costs O(length of word), independent of the dictionary size.
- **Template:** a node holds `children: map char → node` and `is_end: bool`. Insert and search walk character by character.
- **Fails when:** only whole-word lookup is needed (a hash set is simpler), or memory is tight.
- **Alternatives:** a hash set of words or prefixes, sorting plus binary search.

## 22. Bit manipulation
- **Clues:** "without extra space" with pairs or duplicates (XOR), counting set bits, subsets of a small set (bitmask), powers of two, single number.
- **Applies when:** a bitwise property directly answers the question: `x ^ x = 0`, `x & (x-1)` drops the lowest set bit, a mask enumerates subsets.
- **Why it works:** bitwise operations are O(1) and have algebraic identities that cancel or isolate information.
- **Template:** `res = 0; for x: res ^= x` (pairs cancel). `while x: x &= x-1; count++`.
- **Fails when:** readability matters more than micro-gains, or values are large or unbounded.
- **Alternatives:** hashing, math (sum formulas), sorting.

---

## Bottleneck → candidate pattern map
Use this privately to choose the right hint level. **Don't show it to the user during practice.**

| Bottleneck the user found | Candidate patterns |
|---|---|
| Repeated search for a value or complement | Hashing; sort + two pointers; binary search |
| Recomputing sums over overlapping ranges | Prefix sums; sliding window |
| Restarting a contiguous scan after failure | Sliding window |
| Scanning forward to find the next greater or smaller | Monotonic stack |
| Repeatedly finding the min or max of a changing set | Heap; monotonic deque |
| Recursion recomputes the same arguments | DP (memoization) |
| Trying every split or threshold value | Binary search on the answer; DP |
| Checking all pairs of intervals | Sort + intervals sweep |
| Re-exploring nodes | Visited set (DFS/BFS); union-find |
| Many string-prefix comparisons | Trie |

## Constraint → target complexity
Rough guide for "what do the constraints tell you?" (~10^8 simple operations per second):

| n | Usually acceptable |
|---|---|
| ≤ 12 | O(n!) |
| ≤ 20–25 | O(2^n), O(n·2^n) |
| ≤ 500 | O(n³) |
| ≤ 5·10^3 | O(n²) |
| ≤ 10^6 | O(n log n), O(n) |
| > 10^8 or huge values | O(log n), O(1), math |

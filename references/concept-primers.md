# Concept Primers: When the User Doesn't Know a Topic Yet

Use this when the user lacks a **prerequisite**: a data structure or idea that the problem assumes, such as a linked list, recursion, a tree, or Big-O. This is different from a missing *pattern*. Not knowing what a linked list *is* gets a primer. Not seeing that fast/slow pointers apply is normal problem-solving, so use the workflow and the hint ladder.

## Contents
- Detecting a gap
- The primer flow
- Primer checklists by topic
- Returning to the problem

## Detecting a gap

There's a gap when the user:
- says so ("I don't know linked lists", "what's a heap?"),
- misuses the structure's basic operations (for example, treating a linked list as indexable with `head[3]`, or expecting O(1) search in a heap),
- can't trace a tiny example because the structure itself confuses them, or
- is starting their **first problem** on a topic the log has never seen. In that case, ask one readiness question before Step 1: "Have you worked with linked lists before, or should we spend 5 minutes on the basics first?"

Don't assume a gap from one slip. Ask: "Quick check: how would you get to the 3rd node of a linked list?"

## The primer flow

**Pause the problem.** Save it as the *Active problem* in the log, noting the step reached, and say: "Let's take a short detour on linked lists, then come back." A primer is **not a hint** and doesn't lower the problem's score.

Teach interactively, **one idea per message**, and have the user answer each time:

1. **Mental model.** A one-line analogy plus a small ASCII diagram.
   ```
   head → [3 | •] → [7 | •] → [1 | ∅]
   ```
2. **Core operations and their costs.** A small table. Ask the user to *predict* one cost before you show it: "Why is inserting at the head O(1) but finding a value O(n)?"
3. **Pseudocode of the basic operations.** Show the pseudocode for **one** operation (for example, traversal). Then have the user write the pseudocode for a second one themselves (for example, inserting after a node), and check it.
4. **Pitfalls.** The 2–3 classic bugs (see the checklists below). Ask the user to spot one in a 4-line snippet.
5. **Warm-up exercise.** A tiny task the user does in their own language: build a list from an array and print it, count the nodes, find the max. This is practice, not a LeetCode problem, so don't log a score for it.
6. **Readiness check.** One question that combines the ideas: "Given `head`, how would you return the second-to-last node, and how much time and space would it take?"

Keep it short: about 5–8 exchanges. If the user already knows part of it, skip that part.

Log the topic in *Pattern mastery* with status **Learning** and a note: `primer done YYYY-MM-DD`.

## Primer checklists by topic

What the user must be able to do before solving problems on each topic. Claude already knows the content; these lists set the **scope** and the **pitfalls** to check.

| Topic | Must know | Classic pitfalls | Warm-up |
|---|---|---|---|
| **Big-O** | counting operations; nested loops multiply; log n from halving; amortized cost; space versus auxiliary space | assuming a built-in call is O(1) (`list.insert(0,x)`, `in` on a list, string `+=` in a loop) | estimate the cost of 3 short snippets |
| **Arrays / strings** | index access O(1); insert/delete in the middle O(n); slicing copies; immutable strings (in many languages) | off-by-one at the ends; changing a list while iterating over it | reverse an array in place |
| **Hash map / set** | O(1) average get/put/contains; keys must be hashable; no order | using a mutable key; forgetting the default for missing keys | count character frequencies |
| **Linked list** | node = value + next; traverse with `while node`; there is no index; dummy-head trick; doubly linked lists | losing the rest of the list when re-linking (save `next` first); null checks; moving `head` and losing the start | build from an array, print, count |
| **Recursion** | base case, recursive case, trusting the recursive call ("leap of faith"); the call stack uses O(depth) space | missing or wrong base case; not returning the recursive result | factorial, then sum of a list, then reverse a string |
| **Stack / queue** | LIFO vs FIFO; push/pop/peek O(1); a deque for queues (not `list.pop(0)`) | popping an empty stack; using an O(n) dequeue | check balanced `()` only |
| **Binary tree** | node with left/right; height vs depth; preorder/inorder/postorder; level order | confusing a node's value with the node; forgetting the `None` child base case | count nodes, find max depth |
| **BST** | left < node < right **for the whole subtree**; inorder traversal is sorted; O(h) operations | checking only the immediate children | search for a value |
| **Heap** | min/max at the top; push/pop O(log n); peek O(1); search is O(n); built from an array in O(n) | thinking it's fully sorted; your language's default (Python's `heapq` is a min-heap) | the k smallest numbers from a list |
| **Graph** | vertices and edges; adjacency list vs matrix; directed vs undirected; visited sets; grids are implicit graphs | infinite loops without `visited`; marking visited too late in BFS | build an adjacency list from an edge list, list each node's neighbors |
| **Trie** | node = children map + end flag; insert and search walk one character at a time | forgetting the end-of-word flag (a prefix isn't a word) | insert 3 words, check one prefix |
| **Bits** | AND/OR/XOR/shift; `x & 1` gives the parity; `x & (x-1)`; two's complement | sign issues with right shift; precedence of `&` versus `==` | count set bits in a number |
| **DP basics** | the recursion tree has repeats → cache them; a state is "what you need to know to continue" | memoizing on the wrong key | Fibonacci: naive, then memoized, then bottom-up |

## Returning to the problem

After the readiness check, say: "Back to *<problem>*. You were at <step>." Then continue the workflow from that step with one question. If the gap was large, it's fine to switch to an easier first problem on the topic from [problem-progression.md](problem-progression.md) and keep the original as the next one. Tell the user why.

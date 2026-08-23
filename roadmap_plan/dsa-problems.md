# DSA Practice — Full Problem Bank

130 problems, one per weekday across most of Track A (D1–D131, D145–D167),
ordered as a beginner-paced progression (roughly NeetCode150 order):
arrays/hashing → two pointers → sliding window → stacks → binary search →
linked lists → trees → tries/heaps → backtracking → graphs → 1-D DP →
intervals/greedy → 2-D DP → bit manipulation/math → mixed hard review.
Saturdays have no new problem — they link back to the week's Thursday
problem for a from-memory redo (see the phase files). Weeks 23–24
(Phase 5, Raft implementation) and Weeks 29–30 (Phase 6, system-design
real builds) deliberately drop this daily grind — the day's own
algorithmic/systems work already carries that load; see those weeks'
framing in their phase files.

Each entry names the problem, its difficulty/pattern, and a full statement of
what to build — solve it however you like (any language, but do it in Python
to stay consistent with the rest of the roadmap). No solutions here on
purpose; look up the exact problem on LeetCode by title if you want to submit
it there and get test cases for free.

---

## Week 1 (Phase 1) — Arrays & Hashing I

### D1 — Contains Duplicate
*Difficulty: Easy · Pattern: Arrays & Hashing*

Given an integer array `nums`, return `true` if any value appears **at least
twice**, and `false` if every element is distinct.

**Example:** `nums = [1,2,3,1]` → `true`  ·  `nums = [1,2,3,4]` → `false`

### D2 — Valid Anagram
*Difficulty: Easy · Pattern: Hashing*

Given two strings `s` and `t`, return `true` if `t` is an anagram of `s` (same
letters, same counts, any order).

**Example:** `s = "anagram", t = "nagaram"` → `true`  ·  `s = "rat", t = "car"` → `false`

### D3 — Two Sum
*Difficulty: Easy · Pattern: Hashing*

**Warm-up (do this first, ~20 min):** implement a hash table from scratch —
a fixed-size array of buckets, a hash function (`hash(key) % capacity`),
and separate chaining for collisions (`insert`, `get`, `delete`). This is
the one time all year you build the thing Python's `dict` normally hides
from you — every hashing problem after today just uses `dict`/`set`
directly, on purpose, since re-deriving it every time would be noise.

Given an array `nums` and an integer `target`, return the indices of the two
numbers that add up to `target`. Exactly one valid answer exists; you may not
use the same element twice.

**Example:** `nums = [2,7,11,15], target = 9` → `[0,1]`

### D4 — Group Anagrams
*Difficulty: Medium · Pattern: Hashing*

Given an array of strings `strs`, group the anagrams together. Return the
groups in any order.

**Example:** `["eat","tea","tan","ate","nat","bat"]` →
`[["bat"],["nat","tan"],["ate","eat","tea"]]`

### D5 — Top K Frequent Elements
*Difficulty: Medium · Pattern: Hashing / Bucket Sort or Heap*

Given an integer array `nums` and an integer `k`, return the `k` most
frequent elements, in any order. Try to beat the naive `O(n log n)` sort.

**Example:** `nums = [1,1,1,2,2,3], k = 2` → `[1,2]`

---

## Week 2 (Phase 1) — Arrays & Hashing II

### D7 — Product of Array Except Self
*Difficulty: Medium · Pattern: Arrays*

Given an array `nums`, return an array `answer` where `answer[i]` is the
product of all elements of `nums` except `nums[i]` — without using division,
in `O(n)` time.

**Example:** `[1,2,3,4]` → `[24,12,8,6]`

### D8 — Valid Sudoku
*Difficulty: Medium · Pattern: Hashing*

Determine if a 9×9 Sudoku board is valid. Only the filled cells need
checking: each row, each column, and each of the nine 3×3 sub-boxes must
contain the digits 1–9 without repetition.

### D9 — Encode and Decode Strings
*Difficulty: Medium · Pattern: Hashing / String*

Design `encode(list_of_strings) -> str` and `decode(str) -> list_of_strings`
so that any list of strings — including ones containing arbitrary characters
like `#` or `:` — round-trips correctly. (Hint: length-prefix each string
instead of relying on a delimiter character.)

### D10 — Longest Consecutive Sequence
*Difficulty: Medium · Pattern: Hashing*

Given an unsorted array of integers `nums`, return the length of the longest
run of consecutive integers present in the array. Must run in `O(n)` time.

**Example:** `[100,4,200,1,3,2]` → `4` (the run `1,2,3,4`)

### D11 — Valid Palindrome
*Difficulty: Easy · Pattern: Two Pointers*

Given a string `s`, after converting all uppercase letters to lowercase and
removing all non-alphanumeric characters, determine if it reads the same
forwards and backwards.

**Example:** `"A man, a plan, a canal: Panama"` → `true`

---

## Week 3 (Phase 1) — Two Pointers

### D13 — Two Sum II - Input Array Is Sorted
*Difficulty: Medium · Pattern: Two Pointers*

Given a **1-indexed, sorted** array `numbers` and a `target`, return the
1-indexed positions of the two numbers that add up to `target`, using `O(1)`
extra space (two pointers from both ends).

**Example:** `numbers = [2,7,11,15], target = 9` → `[1,2]`

### D14 — 3Sum
*Difficulty: Medium · Pattern: Two Pointers*

Given an integer array `nums`, return all unique triplets `[nums[i], nums[j],
nums[k]]` such that `i != j != k` and the three sum to zero. No duplicate
triplets in the output.

**Example:** `[-1,0,1,2,-1,-4]` → `[[-1,-1,2],[-1,0,1]]`

### D15 — Container With Most Water
*Difficulty: Medium · Pattern: Two Pointers*

Given an array `height` where each value is the height of a vertical line at
that index, find two lines that together with the x-axis form the container
holding the most water. Return the max area.

### D16 — Trapping Rain Water
*Difficulty: Hard · Pattern: Two Pointers*

Given an array `height` representing an elevation map, compute how much
rainwater it can trap after raining.

**Example:** `[0,1,0,2,1,0,1,3,2,1,2,1]` → `6`

### D17 — Best Time to Buy and Sell Stock
*Difficulty: Easy · Pattern: Sliding Window*

Given an array `prices` where `prices[i]` is the stock price on day `i`,
choose one day to buy and a later day to sell to maximize profit. Return `0`
if no profit is possible.

**Example:** `[7,1,5,3,6,4]` → `5` (buy at 1, sell at 6)

---

## Week 4 (Phase 1) — Sliding Window & Stack I

### D19 — Longest Substring Without Repeating Characters
*Difficulty: Medium · Pattern: Sliding Window*

Given a string `s`, find the length of the longest substring without
repeating characters.

**Example:** `"abcabcbb"` → `3` (`"abc"`)

### D20 — Longest Repeating Character Replacement
*Difficulty: Medium · Pattern: Sliding Window*

Given a string `s` and an integer `k`, you may replace up to `k` characters
in the string. Return the length of the longest substring containing the
same letter after replacements.

**Example:** `s = "ABAB", k = 2` → `4`

### D21 — Permutation in String
*Difficulty: Medium · Pattern: Sliding Window*

Given strings `s1` and `s2`, return `true` if `s2` contains a permutation of
`s1` as a contiguous substring.

**Example:** `s1 = "ab", s2 = "eidbaooo"` → `true`

### D22 — Valid Parentheses
*Difficulty: Easy · Pattern: Stack*

**Warm-up (do this first, ~15 min):** implement a stack from scratch,
array-backed (`push`, `pop`, `peek`, `is_empty`, all `O(1)`), then a second
version backed by a singly linked list — and write one sentence on why
Python's `list.append`/`list.pop` already behave like the array-backed
version, which is exactly why you'll use a plain `list` as a stack from
tomorrow on, not reimplement this.

Given a string `s` containing only `(){}[]`, determine if the brackets are
properly matched and nested.

**Example:** `"()[]{}"` → `true`  ·  `"(]"` → `false`

### D23 — Min Stack
*Difficulty: Medium · Pattern: Stack*

Design a stack that supports `push`, `pop`, `top`, and retrieving the
minimum element — all in `O(1)` time.

---

## Week 5 (Phase 2) — Stack II & Binary Search I

### D25 — Evaluate Reverse Polish Notation
*Difficulty: Medium · Pattern: Stack*

Evaluate an arithmetic expression given as tokens in Reverse Polish Notation
(`+ - * /` and integer operands).

**Example:** `["2","1","+","3","*"]` → `9`

### D26 — Generate Parentheses
*Difficulty: Medium · Pattern: Backtracking / Stack*

Given `n` pairs of parentheses, generate all combinations of well-formed
parenthesis strings.

**Example:** `n = 3` → `["((()))","(()())","(())()","()(())","()()()"]`

### D27 — Daily Temperatures
*Difficulty: Medium · Pattern: Monotonic Stack*

Given daily temperatures, return an array `answer` where `answer[i]` is the
number of days you'd have to wait after day `i` for a warmer temperature (0
if there isn't one).

**Example:** `[73,74,75,71,69,72,76,73]` → `[1,1,4,2,1,1,0,0]`

### D28 — Car Fleet
*Difficulty: Medium · Pattern: Monotonic Stack*

Cars are heading to the same destination `target` at different positions and
speeds. A car that catches up to a slower car ahead of it merges into that
car's fleet (never passes). Return the number of fleets that will arrive.

### D29 — Binary Search
*Difficulty: Easy · Pattern: Binary Search*

Given a sorted array of unique integers `nums` and a `target`, return the
index of `target`, or `-1` if it's not present — in `O(log n)`.

---

## Week 6 (Phase 2) — Binary Search II & Linked List I

### D31 — Search a 2D Matrix
*Difficulty: Medium · Pattern: Binary Search*

Given an `m x n` matrix where each row is sorted and the first integer of
each row is greater than the last integer of the previous row, determine if
`target` exists, in `O(log(m·n))`.

### D32 — Koko Eating Bananas
*Difficulty: Medium · Pattern: Binary Search on Answer*

Koko has `piles` of bananas and `h` hours before the guards return. Each
hour she picks one pile and eats up to `k` bananas from it. Find the minimum
integer `k` so she finishes all piles within `h` hours.

### D33 — Find Minimum in Rotated Sorted Array
*Difficulty: Medium · Pattern: Binary Search*

Given a rotated sorted array of unique elements, find the minimum element in
`O(log n)`.

### D34 — Search in Rotated Sorted Array
*Difficulty: Medium · Pattern: Binary Search*

Given a rotated sorted array of unique integers and a `target`, return its
index, or `-1`, in `O(log n)`.

### D35 — Reverse Linked List
*Difficulty: Easy · Pattern: Linked List*

**Warm-up (do this first, ~20 min):** implement a singly linked list from
scratch — a `Node` class (`value`, `next`) and a `LinkedList` class with
`insert_head`, `insert_tail`, `delete(value)`, and `traverse()`. Every
linked-list problem for the next 3 weeks assumes you can picture `Node`
and pointer reassignment without hesitating — this is where that muscle
memory gets built.

Given the head of a singly linked list, reverse it and return the new head.

---

## Week 7 (Phase 2) — Linked List II

### D37 — Merge Two Sorted Lists
*Difficulty: Easy · Pattern: Linked List*

Merge two sorted linked lists into one sorted list by splicing the existing
nodes together (no new nodes).

### D38 — Reorder List
*Difficulty: Medium · Pattern: Linked List*

Given `L0 → L1 → … → Ln`, reorder it in place to
`L0 → Ln → L1 → Ln-1 → L2 → Ln-2 → …`.

### D39 — Remove Nth Node From End of List
*Difficulty: Medium · Pattern: Linked List / Two Pointers*

Given the head of a linked list, remove the `n`th node from the end and
return the head. Try to do it in one pass.

### D40 — Copy List with Random Pointer
*Difficulty: Medium · Pattern: Linked List / Hashing*

Each node in a linked list has an extra `random` pointer that can point to
any node in the list or `null`. Return a deep copy of the list.

### D41 — Add Two Numbers
*Difficulty: Medium · Pattern: Linked List*

Two non-empty linked lists represent two non-negative integers with digits
stored in **reverse order**. Add the numbers and return the sum as a linked
list.

---

## Week 8 (Phase 2) — Linked List III & Trees I

### D43 — Linked List Cycle
*Difficulty: Easy · Pattern: Two Pointers (Floyd's)*

Given the head of a linked list, determine if it has a cycle, using `O(1)`
extra space.

### D44 — Find the Duplicate Number
*Difficulty: Medium · Pattern: Binary Search / Fast-Slow Pointers*

Given an array of `n + 1` integers where each value is in `[1, n]`, and
exactly one value repeats (possibly more than once), find it — without
modifying the array and using `O(1)` extra space.

### D45 — LRU Cache
*Difficulty: Medium · Pattern: Linked List + Hash Map*

Design a Least Recently Used cache with `get(key)` and `put(key, value)`
both running in `O(1)` average time.

### D46 — Invert Binary Tree
*Difficulty: Easy · Pattern: Trees*

Given the root of a binary tree, invert it (mirror left/right at every node)
and return the root.

### D47 — Maximum Depth of Binary Tree
*Difficulty: Easy · Pattern: Trees*

Given the root of a binary tree, return its maximum depth (the longest
root-to-leaf path, counted in nodes).

---

## Week 9 (Phase 3) — Trees II

### D49 — Diameter of Binary Tree
*Difficulty: Easy · Pattern: Trees*

Return the length (in edges) of the longest path between any two nodes in
the tree — the path may or may not pass through the root.

### D50 — Balanced Binary Tree
*Difficulty: Easy · Pattern: Trees*

Determine if a binary tree is height-balanced: for every node, the heights
of its left and right subtrees differ by at most 1.

### D51 — Same Tree
*Difficulty: Easy · Pattern: Trees*

Given the roots of two binary trees, check if they are structurally
identical with the same node values.

### D52 — Subtree of Another Tree
*Difficulty: Easy · Pattern: Trees*

Given the roots of two binary trees `root` and `subRoot`, return `true` if
there's a subtree of `root` with the same structure and values as `subRoot`.

### D53 — Lowest Common Ancestor of a BST
*Difficulty: Medium · Pattern: Trees / BST*

Given a binary search tree and two of its nodes `p` and `q`, find their
lowest common ancestor.

---

## Week 10 (Phase 3) — Trees III

### D55 — Binary Tree Level Order Traversal
*Difficulty: Medium · Pattern: Trees / BFS*

**Warm-up (do this first, ~20 min):** implement a queue from scratch, two
ways — (1) backed by your Week-4 linked list (`enqueue` at tail, `dequeue`
at head, both `O(1)`), and (2) the classic "two stacks" queue, using
Week-4's stack — then explain out loud why a list-backed queue
(`list.pop(0)`) is `O(n)` and should never be your first choice. This is
the last from-scratch structure this year; `collections.deque` is what
you'll actually reach for starting today's BFS below and every graph
problem after it.

Return the level-order traversal of a binary tree's values (left to right,
level by level) as a list of lists.

### D56 — Binary Tree Right Side View
*Difficulty: Medium · Pattern: Trees / BFS*

Return the values visible when looking at the tree from the right side,
ordered top to bottom.

### D57 — Count Good Nodes in Binary Tree
*Difficulty: Medium · Pattern: Trees / DFS*

A node `X` is "good" if no node on the path from the root to `X` has a value
greater than `X`. Count the good nodes.

### D58 — Validate Binary Search Tree
*Difficulty: Medium · Pattern: Trees / BST*

Given the root of a binary tree, determine if it is a valid BST.

### D59 — Kth Smallest Element in a BST
*Difficulty: Medium · Pattern: Trees / BST*

Given the root of a BST and an integer `k`, return the `k`th smallest value
(1-indexed) among all node values.

---

## Week 11 (Phase 3) — Trees IV, Tries, Heap I

### D61 — Construct Binary Tree from Preorder and Inorder Traversal
*Difficulty: Medium · Pattern: Trees*

Given two integer arrays `preorder` and `inorder` (unique values), construct
and return the binary tree they represent.

### D62 — Binary Tree Maximum Path Sum
*Difficulty: Hard · Pattern: Trees / DFS*

Return the maximum sum of any non-empty path in the tree. A path can start
and end at any node and need not pass through the root.

### D63 — Serialize and Deserialize Binary Tree
*Difficulty: Hard · Pattern: Trees*

Design `serialize(root) -> str` and `deserialize(str) -> root` so a binary
tree round-trips through a string exactly.

### D64 — Implement Trie (Prefix Tree)
*Difficulty: Medium · Pattern: Tries*

Implement a Trie with `insert(word)`, `search(word)`, and
`startsWith(prefix)`.

### D65 — Design Add and Search Words Data Structure
*Difficulty: Medium · Pattern: Tries*

Design a structure supporting `addWord(word)` and `search(word)`, where
`search` may contain `.` as a wildcard matching any single letter.

---

## Week 12 (Phase 3) — Heap II & Backtracking I

### D67 — Kth Largest Element in a Stream
*Difficulty: Easy · Pattern: Heap*

Design a class that, given `k` and an initial stream of numbers, supports
`add(val)` returning the `k`th largest element after each addition.

### D68 — Last Stone Weight
*Difficulty: Easy · Pattern: Heap*

You have stones with positive weights. Repeatedly smash the two heaviest
together: if equal, both are destroyed; otherwise the difference remains.
Return the weight of the last stone left, or `0`.

### D69 — K Closest Points to Origin
*Difficulty: Medium · Pattern: Heap*

Given an array of 2D points and an integer `k`, return the `k` points
closest to the origin `(0,0)`.

### D70 — Kth Largest Element in an Array
*Difficulty: Medium · Pattern: Heap / Quickselect*

Given an integer array `nums` and integer `k`, return the `k`th largest
element in sorted order (not the `k`th distinct value).

### D71 — Task Scheduler
*Difficulty: Medium · Pattern: Heap / Greedy*

Given a list of CPU `tasks` and a cooldown `n` between two same tasks,
return the minimum number of CPU intervals (including idle slots) needed to
finish all tasks.

---

## Week 13 (Phase 3) — Backtracking II & Graphs I

### D73 — Subsets
*Difficulty: Medium · Pattern: Backtracking*

Given an array `nums` of unique integers, return all possible subsets (the
power set), with no duplicates.

### D74 — Combination Sum
*Difficulty: Medium · Pattern: Backtracking*

Given a distinct array `candidates` and a `target`, return all unique
combinations that sum to `target`. Each number may be reused unlimited
times.

### D75 — Permutations
*Difficulty: Medium · Pattern: Backtracking*

Given an array `nums` of distinct integers, return all possible
permutations.

### D76 — Subsets II
*Difficulty: Medium · Pattern: Backtracking*

Given an integer array `nums` that **may contain duplicates**, return all
possible unique subsets.

### D77 — Word Search
*Difficulty: Medium · Pattern: Backtracking*

Given an `m x n` grid of characters and a `word`, return `true` if the word
can be constructed from letters of sequentially adjacent cells (no cell
reused).

---

## Week 14 (Phase 4) — Graphs II

### D79 — Number of Islands
*Difficulty: Medium · Pattern: Graphs / DFS-BFS*

Given an `m x n` binary grid (`'1'` = land, `'0'` = water), return the number
of islands (4-directionally connected land regions).

### D80 — Max Area of Island
*Difficulty: Medium · Pattern: Graphs*

Given a binary grid, return the area of the largest island (`0` if there is
none).

### D81 — Clone Graph
*Difficulty: Medium · Pattern: Graphs*

Given a reference node in a connected undirected graph, return a deep copy
(clone) of the entire graph.

### D82 — Islands and Treasure (Walls and Gates)
*Difficulty: Medium · Pattern: Graphs / BFS*

Given a grid of rooms (`INF` = empty room, `-1` = wall, `0` = gate), fill
each empty room with the distance to its nearest gate.

### D83 — Rotting Oranges
*Difficulty: Medium · Pattern: Graphs / BFS*

A grid has `0` empty, `1` fresh orange, `2` rotten orange. Every minute, a
rotten orange rots its fresh 4-directional neighbors. Return the minimum
minutes until no fresh orange remains, or `-1` if impossible.

---

## Week 15 (Phase 4) — Graphs III

### D85 — Pacific Atlantic Water Flow
*Difficulty: Medium · Pattern: Graphs*

Given an `m x n` matrix of heights, water can flow from a cell to a
neighbor with equal or lower height. Find all cells from which water can
reach **both** the Pacific (top/left edges) and Atlantic (bottom/right
edges).

### D86 — Surrounded Regions
*Difficulty: Medium · Pattern: Graphs*

Given a board of `'X'` and `'O'`, flip every `'O'` that is fully surrounded
by `'X'` (not connected to a border `'O'`) into `'X'`, in place.

### D87 — Course Schedule
*Difficulty: Medium · Pattern: Graphs / Topological Sort*

Given `numCourses` and a list of prerequisite pairs, determine if it's
possible to finish all courses (i.e., the prerequisite graph has no cycle).

### D88 — Course Schedule II
*Difficulty: Medium · Pattern: Graphs / Topological Sort*

Same setup as Course Schedule, but return a valid course order, or an empty
array if it's impossible.

### D89 — Redundant Connection
*Difficulty: Medium · Pattern: Graphs / Union-Find*

A graph started as a tree with `n` nodes, then one extra edge was added,
creating exactly one cycle. Return that redundant edge.

---

## Week 16 (Phase 4) — Graphs IV & Advanced Graphs I

### D91 — Number of Connected Components in an Undirected Graph
*Difficulty: Medium · Pattern: Union-Find*

Given `n` nodes and a list of undirected edges, return the number of
connected components.

### D92 — Graph Valid Tree
*Difficulty: Medium · Pattern: Union-Find*

Given `n` nodes and a list of undirected edges, determine whether the edges
form a valid tree (connected, and no cycles).

### D93 — Word Ladder
*Difficulty: Hard · Pattern: Graphs / BFS*

Given `beginWord`, `endWord`, and a word list, return the length of the
shortest transformation sequence where each step changes exactly one letter
and every intermediate word must be in the word list.

### D94 — Reconstruct Itinerary
*Difficulty: Hard · Pattern: Graphs / Eulerian Path*

Given a list of airline tickets `[from, to]`, reconstruct the itinerary
starting from `"JFK"` that uses every ticket exactly once, returning the
lexicographically smallest valid itinerary.

### D95 — Min Cost to Connect All Points
*Difficulty: Medium · Pattern: Graphs / Minimum Spanning Tree*

Given points on a 2D plane, connect all points using edges weighted by
Manhattan distance, minimizing total cost (build a Minimum Spanning Tree).

---

## Week 17 (Phase 4) — Advanced Graphs II & 1-D DP I

### D97 — Network Delay Time
*Difficulty: Medium · Pattern: Dijkstra*

Given `n` nodes and directed weighted edges `(u, v, w)` representing travel
times, and a starting node `k`, return the time for a signal from `k` to
reach every node, or `-1` if it can't reach all of them.

### D98 — Swim in Rising Water
*Difficulty: Hard · Pattern: Dijkstra / Binary Search*

Given an `n x n` grid of elevations, water rises over time; at time `t` you
may only step on cells with elevation `≤ t`. Find the minimum `t` at which
you can swim from top-left to bottom-right.

### D99 — Climbing Stairs
*Difficulty: Easy · Pattern: 1-D DP*

You're climbing `n` stairs; each step you may climb 1 or 2 stairs. Return
the number of distinct ways to reach the top.

### D100 — Min Cost Climbing Stairs
*Difficulty: Easy · Pattern: 1-D DP*

Given `cost[i]`, the cost of stepping on stair `i`, you may start at index 0
or 1 and always move 1 or 2 indices forward. Return the minimum cost to
reach the top.

### D101 — House Robber
*Difficulty: Medium · Pattern: 1-D DP*

Houses in a row hold money; you can't rob two adjacent houses. Return the
maximum amount you can rob.

---

## Week 18 (Phase 4) — 1-D DP II

### D103 — House Robber II
*Difficulty: Medium · Pattern: 1-D DP*

Same as House Robber, but the houses are arranged in a **circle** (first and
last house are adjacent).

### D104 — Longest Palindromic Substring
*Difficulty: Medium · Pattern: 1-D DP / Two Pointers*

Given a string `s`, return the longest substring of `s` that is a
palindrome.

### D105 — Palindromic Substrings
*Difficulty: Medium · Pattern: 1-D DP / Two Pointers*

Given a string `s`, return the number of palindromic substrings (different
start/end positions count separately, even if the text repeats).

### D106 — Decode Ways
*Difficulty: Medium · Pattern: 1-D DP*

A string of digits encodes a message where `'A'..'Z'` map to `1..26`. Given
the digit string, return the number of ways it can be decoded.

### D107 — Coin Change
*Difficulty: Medium · Pattern: 1-D DP*

Given coin denominations and a target `amount`, return the fewest coins
needed to make that amount, or `-1` if it can't be made.

---

## Week 19 (Phase 5) — 1-D DP III & Intervals I

### D109 — Maximum Product Subarray
*Difficulty: Medium · Pattern: 1-D DP*

Given an integer array `nums`, find a contiguous subarray with the largest
product and return that product.

### D110 — Word Break
*Difficulty: Medium · Pattern: 1-D DP*

Given a string `s` and a dictionary of words, return `true` if `s` can be
segmented into a space-separated sequence of dictionary words.

### D111 — Longest Increasing Subsequence
*Difficulty: Medium · Pattern: 1-D DP*

Given an integer array `nums`, return the length of the longest strictly
increasing subsequence.

### D112 — Partition Equal Subset Sum
*Difficulty: Medium · Pattern: 1-D DP*

Given an integer array `nums`, determine if it can be partitioned into two
subsets with equal sum.

### D113 — Insert Interval
*Difficulty: Medium · Pattern: Intervals*

Given a list of non-overlapping intervals sorted by start time and a new
interval, insert it (merging as needed) and return the resulting list.

---

## Week 20 (Phase 5) — Intervals II & Greedy I

### D115 — Merge Intervals
*Difficulty: Medium · Pattern: Intervals*

Given an array of intervals, merge all overlapping intervals and return the
result.

### D116 — Non-overlapping Intervals
*Difficulty: Medium · Pattern: Intervals / Greedy*

Given an array of intervals, return the minimum number you'd need to remove
so the rest don't overlap.

### D117 — Meeting Rooms
*Difficulty: Easy · Pattern: Intervals*

Given an array of meeting time intervals, determine if one person could
attend every meeting (i.e., no two overlap).

### D118 — Meeting Rooms II
*Difficulty: Medium · Pattern: Intervals / Heap*

Given an array of meeting time intervals, return the minimum number of
conference rooms required.

### D119 — Maximum Subarray
*Difficulty: Medium · Pattern: Greedy / Kadane's*

Given an integer array `nums`, find the contiguous subarray with the largest
sum and return that sum.

---

## Week 21 (Phase 5) — Greedy II & 2-D DP I

### D121 — Jump Game
*Difficulty: Medium · Pattern: Greedy*

Each element of `nums` is your maximum jump length from that position,
starting at index 0. Determine if you can reach the last index.

### D122 — Jump Game II
*Difficulty: Medium · Pattern: Greedy*

Same setup as Jump Game (guaranteed reachable) — return the minimum number
of jumps to reach the last index.

### D123 — Gas Station
*Difficulty: Medium · Pattern: Greedy*

Given `gas[i]` and `cost[i]` for a circular route of gas stations, find the
starting station index from which you can complete the circuit once, or
`-1` if impossible (a unique answer is guaranteed if one exists).

### D124 — Hand of Straights
*Difficulty: Medium · Pattern: Greedy*

Given an array of card values and a group size `groupSize`, determine if the
cards can be rearranged into groups of `groupSize` **consecutive** values.

### D125 — Unique Paths
*Difficulty: Medium · Pattern: 2-D DP*

A robot on an `m x n` grid starts top-left and can only move right or down.
Return the number of unique paths to the bottom-right corner.

---

## Week 22 (Phase 5) — 2-D DP II

### D127 — Longest Common Subsequence
*Difficulty: Medium · Pattern: 2-D DP*

Given two strings, return the length of their longest common subsequence
(`0` if they share none).

### D128 — Best Time to Buy and Sell Stock with Cooldown
*Difficulty: Medium · Pattern: 2-D DP*

Given daily stock `prices`, maximize profit with unlimited transactions, but
after selling you must wait one day (cooldown) before buying again.

### D129 — Coin Change II
*Difficulty: Medium · Pattern: 2-D DP*

Given coin denominations and a target `amount`, return the number of
distinct **combinations** (order doesn't matter) that make up that amount.

### D130 — Target Sum
*Difficulty: Medium · Pattern: 2-D DP*

Given an integer array `nums` and an integer `target`, assign `+` or `-` to
each number so the expression evaluates to `target`. Return the number of
ways to do this.

### D131 — Interleaving String
*Difficulty: Medium · Pattern: 2-D DP*

Given strings `s1`, `s2`, `s3`, determine if `s3` is formed by interleaving
`s1` and `s2` while preserving the relative order of characters from each.

---

## Week 25 (Phase 6) — 2-D DP III & Bit Manipulation I

### D145 — Longest Increasing Path in a Matrix
*Difficulty: Hard · Pattern: DFS + Memoization*

Given an `m x n` matrix, return the length of the longest strictly
increasing path, moving up/down/left/right.

### D146 — Distinct Subsequences
*Difficulty: Hard · Pattern: 2-D DP*

Given strings `s` and `t`, return the number of distinct subsequences of `s`
that equal `t`.

### D147 — Edit Distance
*Difficulty: Medium · Pattern: 2-D DP*

Given `word1` and `word2`, return the minimum number of insert/delete/
replace operations to convert `word1` into `word2`.

### D148 — Single Number
*Difficulty: Easy · Pattern: Bit Manipulation*

Given a non-empty array where every element appears twice except for one,
find that single element. (XOR is your friend.)

### D149 — Number of 1 Bits
*Difficulty: Easy · Pattern: Bit Manipulation*

Given an unsigned integer, return the number of `1` bits in its binary
representation (Hamming weight).

---

## Week 26 (Phase 6) — Bit Manipulation II & Math/Geometry I

### D151 — Counting Bits
*Difficulty: Easy · Pattern: Bit Manipulation / DP*

Given `n`, return an array `ans` where `ans[i]` is the number of `1` bits in
`i`, for every `0 ≤ i ≤ n`.

### D152 — Reverse Bits
*Difficulty: Easy · Pattern: Bit Manipulation*

Reverse the bits of a given 32-bit unsigned integer.

### D153 — Missing Number
*Difficulty: Easy · Pattern: Bit Manipulation / Math*

Given an array containing `n` distinct numbers from `0` to `n`, find the one
number missing from the range.

### D154 — Rotate Image
*Difficulty: Medium · Pattern: Math / Matrix*

Given an `n x n` 2D matrix representing an image, rotate it 90 degrees
clockwise **in place**.

### D155 — Spiral Matrix
*Difficulty: Medium · Pattern: Math / Matrix*

Given an `m x n` matrix, return all its elements in spiral order.

---

## Week 27 (Phase 6) — Math/Geometry II

### D157 — Set Matrix Zeroes
*Difficulty: Medium · Pattern: Matrix*

Given an `m x n` matrix, if an element is `0`, set its entire row and column
to `0`. Bonus: do it with `O(1)` extra space.

### D158 — Happy Number
*Difficulty: Easy · Pattern: Math / Hashing*

Repeatedly replace a number with the sum of the squares of its digits. If
this reaches `1`, the number is "happy." Determine if a given number is
happy (watch for infinite loops).

### D159 — Plus One
*Difficulty: Easy · Pattern: Math*

Given a large integer represented as an array of digits, increment the
integer by one and return the resulting array.

### D160 — Pow(x, n)
*Difficulty: Medium · Pattern: Math / Binary Exponentiation*

Implement `pow(x, n)` — compute `x` raised to the power `n` in `O(log n)`
time.

### D161 — Merge Sorted Array
*Difficulty: Easy · Pattern: Two Pointers*

Given two sorted arrays `nums1` (with extra trailing space) and `nums2`,
merge `nums2` into `nums1` in place as one sorted array.

---

## Week 28 (Phase 6) — Mixed Hard Review

### D163 — Design Twitter
*Difficulty: Medium · Pattern: Design / Heap*

Design a simplified Twitter: post tweets, follow/unfollow users, and
retrieve the 10 most recent tweet IDs in a user's news feed (their own posts
plus everyone they follow).

### D164 — LFU Cache
*Difficulty: Hard · Pattern: Design / Hashing*

Design a Least Frequently Used cache with `get`/`put` in `O(1)` average
time; on eviction, remove the least frequently used key, breaking ties by
least recently used.

### D165 — Word Search II
*Difficulty: Hard · Pattern: Backtracking + Trie*

Given an `m x n` board of characters and a list of `words`, return every
word that can be built from sequentially adjacent cells (no cell reused per
word). Build a Trie of the word list first — this is the payoff for Week
11's Trie problems.

### D166 — Merge k Sorted Lists
*Difficulty: Hard · Pattern: Heap / Divide & Conquer*

Given an array of `k` sorted linked lists, merge them into one sorted list.

### D167 — Alien Dictionary
*Difficulty: Hard · Pattern: Graphs / Topological Sort*

Given a list of words that are sorted lexicographically according to the
rules of some unknown alien alphabet, derive the ordering of letters in that
alphabet.

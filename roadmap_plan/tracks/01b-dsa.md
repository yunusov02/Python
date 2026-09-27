# Track 1B — Data Structures & Algorithms (Python)

**Goal:** go from near-zero DSA to solving LeetCode Mediums comfortably and
explaining your reasoning out loud like in a real interview. Topics follow
the NeetCode roadmap order, with a Foundations module first.

**Required knowledge:** Python fundamentals. Modules 1A.1–1A.4 (Git/venv,
functions & closures, memory model, iterators/generators) help but are not
blockers.

**Total:** ~280 hours · ~196 problems (all NeetCode 150 + Easy warm-ups +
build-from-scratch exercises + Foundations problems).

**Resources used throughout:**
- NeetCode — *Algorithms & Data Structures for Beginners* (neetcode.io/courses)
  and *Advanced Algorithms* (same page) for Two Pointers, Sliding Window,
  Prefix Sums, Kadane's.
- NeetCode problem videos — neetcode.io/practice (every NeetCode 150 problem
  has an explanation video linked there).
- *Grokking Algorithms*, 2nd ed. (Aditya Bhargava, 2023).
- Python time complexity of built-ins — wiki.python.org/moin/TimeComplexity.

---

## How to use this file

### Rules

> **STUCK RULE.** Give every problem an honest **25–30 minute** attempt
> (write brute force first if nothing else comes). If you are still stuck,
> watch the NeetCode explanation video, **close it**, and do not copy code.
> Re-solve the problem **from a blank file the next day**. Only then tick
> "Solved".

> **SPACED REPETITION RULE.** Redo every solved problem **from a blank file**
> after **1, 3 and 7 days**. Tick R1 / R3 / R7 when the redo passes all tests
> without looking at your old solution. If a redo fails, reset: the next
> redo is again 1 day later.

> **NO SOLUTIONS HERE.** This file only contains problem statements, the
> pattern name and what you must be able to explain. Solutions live only in
> your own files.

### Where your code goes

`dsa/<NN-topic>/<slug>.py`, e.g. `dsa/01-arrays-hashing/two_sum.py`. Each file:

1. a module docstring with the problem statement (copy it from here);
2. the solution function(s);
3. a `tests()` function with plain `assert` statements (normal cases + edge
   cases: empty input, one element, duplicates, negatives…);
4. `tests()` called at module level — run with `python3 dsa/<NN-topic>/<slug>.py`.

No pytest here — plain asserts on purpose.

### Legend

- **Easy / Medium / Hard** — LeetCode difficulty.
- **OPTIONAL** — Hard problems at the end of a module. Do them on the second
  pass or when the module's Mediums feel easy.
- **Build** — implement a data structure from scratch (no LeetCode link).
- Each problem has this checkbox row:
  `- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7`
  (Solved = passed from a blank file; R1/R3/R7 = spaced-repetition redos.)
- Each theory lesson and each "must be able to explain" item is a checkbox too.

### How to solve every problem (interview habit)

1. Restate the problem and ask about constraints/edge cases.
2. Say the brute force and its Big O out loud.
3. Find the bottleneck and name the pattern that removes it.
4. Code it, then dry-run one example by hand.
5. State final time and space complexity.

---

## Module 0 — Foundations (~25h)

**Topics:** Big O (time and space, best/worst/average, amortized), how
arrays live in memory (static vs dynamic arrays), Python `list`/`str`
operation costs, strings and immutability, recursion and the call stack
(base case, recursion depth, stack overflow), sorting by hand (insertion
sort, merge sort, quick sort), binary search, prefix sums.

### Theory

- [ ] **0.T1 Big O notation** — *Grokking Algorithms* ch.1 "Introduction to
  algorithms" (Big O section); wiki.python.org/moin/TimeComplexity (read the
  `list`, `dict`, `set` tables).
- [ ] **0.T2 Arrays in memory** — NeetCode Beginners: "RAM", "Static Arrays",
  "Dynamic Arrays"; *Grokking* ch.2 "Selection sort" (arrays vs linked lists
  section).
- [ ] **0.T3 Recursion and the call stack** — *Grokking* ch.3 "Recursion";
  NeetCode Beginners: "Factorial", "Fibonacci" (recursion section).
- [ ] **0.T4 Sorting I: insertion sort and merge sort** — NeetCode Beginners:
  "Insertion Sort", "Merge Sort".
- [ ] **0.T5 Sorting II: quick sort and divide & conquer** — *Grokking* ch.4
  "Quicksort"; NeetCode Beginners: "Quick Sort", "Bucket Sort".
- [ ] **0.T6 Binary search** — *Grokking* ch.1 (binary search section);
  NeetCode Beginners: "Search Array", "Search Range".
- [ ] **0.T7 Prefix sums** — NeetCode Advanced Algorithms: "Prefix Sums".

### Problems

#### 0.1 Concatenation of Array — Easy — Arrays  [LC 1929](https://leetcode.com/problems/concatenation-of-array/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Given an integer array `nums` of length `n`, return an array
`ans` of length `2n` where `ans[i] == nums[i]` and `ans[i + n] == nums[i]`.
Example: `nums = [1,2,1]` → `[1,2,1,1,2,1]`.

**Must be able to explain:**
- [ ] The cost of building the result with `append` in a loop vs pre-allocating a list of size `2n`.
- [ ] Time and space complexity.
- [ ] What "amortized O(1) append" means for a dynamic array.

#### 0.2 Remove Element — Easy — Arrays (in place)  [LC 27](https://leetcode.com/problems/remove-element/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Given an array `nums` and a value `val`, remove all occurrences
of `val` **in place** and return `k`, the number of remaining elements. The
first `k` slots must contain the kept elements (order may change). Example:
`nums = [3,2,2,3], val = 3` → `k = 2`, `nums` starts with `[2,2]`.

**Must be able to explain:**
- [ ] Why `list.remove()` in a loop is O(n²).
- [ ] What "in place, O(1) extra space" means.
- [ ] Edge cases: empty array, all elements equal `val`, no element equals `val`.

#### 0.3 Reverse String — Easy — Strings / Arrays  [LC 344](https://leetcode.com/problems/reverse-string/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Reverse a list of characters `s` in place with O(1) extra
memory. Example: `["h","e","l","l","o"]` → `["o","l","l","e","h"]`.

**Must be able to explain:**
- [ ] Why Python `str` cannot be modified in place (immutability) and why the input is a list.
- [ ] Why `s[::-1]` does not satisfy "O(1) extra memory".
- [ ] Time and space complexity of your version.

#### 0.4 Fibonacci Number — Easy — Recursion  [LC 509](https://leetcode.com/problems/fibonacci-number/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** `F(0) = 0`, `F(1) = 1`, `F(n) = F(n-1) + F(n-2)`. Given `n`,
return `F(n)`. Example: `n = 4` → `3`. Write a **plain recursive** version
first, then a second version that avoids repeated work.

**Must be able to explain:**
- [ ] Draw the recursion tree for `n = 5` and count the calls.
- [ ] Why the naive recursion is exponential.
- [ ] What happens to the call stack for large `n` (and Python's recursion limit).

#### 0.5 Power of Two — Easy — Recursion  [LC 231](https://leetcode.com/problems/power-of-two/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Given an integer `n`, return `True` if `n` is a power of two.
Example: `n = 16` → `True`, `n = 6` → `False`. Solve it **recursively**
(bit tricks come in Module 17).

**Must be able to explain:**
- [ ] The base case(s) and the recursive case.
- [ ] Recursion depth as a function of `n` (O(log n)).
- [ ] Edge cases: `0`, `1`, negative numbers.

#### 0.6 Sort an Array with merge sort — Medium — Sorting (Build)  [LC 912](https://leetcode.com/problems/sort-an-array/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Sort an integer array in ascending order **without** using
`sorted()`/`list.sort()`. Implement **merge sort** yourself. Example:
`[5,2,3,1]` → `[1,2,3,5]`.

**Must be able to explain:**
- [ ] The split step and the merge step, drawn on paper for 8 elements.
- [ ] Why the time is O(n log n) in every case (count levels × work per level).
- [ ] Extra space used and why merge sort is stable.

#### 0.7 Sort an Array with quick sort — Medium — Sorting (Build)  [LC 912](https://leetcode.com/problems/sort-an-array/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Same problem as 0.6, but implement **quick sort** (in place,
with a partition function). Example: `[5,1,1,2,0,0]` → `[0,0,1,1,2,5]`.

**Must be able to explain:**
- [ ] What the partition step guarantees after it finishes.
- [ ] Best/average vs worst case, and which input produces the worst case.
- [ ] Why pivot choice (first / last / random) matters; stable or not?

#### 0.8 Sort Colors — Medium — Partitioning  [LC 75](https://leetcode.com/problems/sort-colors/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** An array contains only `0`, `1` and `2`. Sort it in place so
equal values are adjacent, in order 0, 1, 2, without a library sort.
Example: `[2,0,2,1,1,0]` → `[0,0,1,1,2,2]`.

**Must be able to explain:**
- [ ] A two-pass counting approach and its complexity.
- [ ] How a one-pass approach relates to quick sort's partition.
- [ ] The invariant each pointer maintains.

#### 0.9 Search Insert Position — Easy — Binary Search  [LC 35](https://leetcode.com/problems/search-insert-position/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Given a sorted array of distinct integers and a `target`,
return its index if found, otherwise the index where it would be inserted.
Must be O(log n). Example: `nums = [1,3,5,6], target = 2` → `1`.

**Must be able to explain:**
- [ ] The loop condition (`<` vs `<=`) and how `lo`/`hi` move.
- [ ] What the final value of `lo` means when the target is missing.
- [ ] Why the problem requires a sorted input.

#### 0.10 Running Sum of 1d Array — Easy — Prefix Sums  [LC 1480](https://leetcode.com/problems/running-sum-of-1d-array/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return `runningSum` where `runningSum[i] = nums[0] + … + nums[i]`.
Example: `[1,2,3,4]` → `[1,3,6,10]`.

**Must be able to explain:**
- [ ] The difference between recomputing every sum (O(n²)) and reusing the previous one.
- [ ] Doing it in place vs into a new list.

#### 0.11 Range Sum Query – Immutable — Easy — Prefix Sums  [LC 303](https://leetcode.com/problems/range-sum-query-immutable/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Design a class `NumArray(nums)` with `sumRange(left, right)`
returning the sum of `nums[left..right]` inclusive. Many queries will be
made. Example: `nums = [-2,0,3,-5,2,-1]`, `sumRange(0, 2)` → `1`,
`sumRange(2, 5)` → `-1`.

**Must be able to explain:**
- [ ] The cost of the constructor vs the cost of each query.
- [ ] Off-by-one handling when `left = 0`.
- [ ] Why this trick does not work directly if `nums` can be updated.

#### 0.12 Find Pivot Index — Easy — Prefix Sums  [LC 724](https://leetcode.com/problems/find-pivot-index/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the leftmost index where the sum of elements strictly to
the left equals the sum strictly to the right; `-1` if none. Example:
`[1,7,3,6,5,6]` → `3`.

**Must be able to explain:**
- [ ] How a total sum plus a running left sum gives the right sum.
- [ ] Edge cases: pivot at index 0 or at the last index; negative numbers.
- [ ] Time and space complexity.

### Module checklist — I can…
- [ ] State the Big O of common Python operations (`list.append`, `list.insert(0, x)`, `x in list`, `x in set`, slicing, `str` concatenation in a loop).
- [ ] Explain the difference between time and space complexity, and amortized cost.
- [ ] Trace a recursive function on paper and draw its call stack.
- [ ] Write merge sort and quick sort from a blank file and state their complexities.
- [ ] Write an off-by-one-free binary search from a blank file.
- [ ] Build a prefix-sum array and answer range queries in O(1).

**Estimated hours:** ~25h

### Self-check interview questions
1. What does O(n log n) mean, and name two algorithms with that complexity.
2. Why is `list.insert(0, x)` O(n) but `list.append(x)` amortized O(1)?
3. What is a stack overflow in the context of recursion, and what is Python's default recursion limit?
4. Compare merge sort and quick sort: time, space, stability, worst case.
5. Why does binary search need sorted input, and what is its complexity?
6. What problem do prefix sums solve?
7. Why is repeated string concatenation in a loop potentially slow in Python?

---

**Answers**
1. The running time grows proportionally to n × log n. Merge sort, heap sort, average-case quick sort.
2. `insert(0, x)` shifts every existing element one slot right. `append` writes at the end; the underlying array over-allocates, so occasional resize copies average out to O(1) per append.
3. Each call adds a frame to the call stack; too many nested calls exhaust it. CPython raises `RecursionError` at the default limit of 1000 frames (`sys.getrecursionlimit()`).
4. Merge sort: O(n log n) always, O(n) extra space, stable. Quick sort: O(n log n) average, O(n²) worst case (bad pivots), O(log n) stack space, not stable in its usual in-place form.
5. Each comparison discards half of the remaining range, which is only valid if order tells you which half can contain the target. O(log n).
6. Answering many range-sum queries fast: after an O(n) precomputation, each query is O(1).
7. `str` is immutable, so each `+` may create a new string and copy the old content, giving O(n²) total. `"".join(parts)` builds the result once.

---

## Module 1 — Arrays & Hashing (~16h)

**Topics:** hash functions, buckets, collisions (separate chaining vs open
addressing), load factor and resizing, Python `dict`/`set`/`Counter`/
`defaultdict`, frequency counting, hashing as a way to trade space for time,
bucket sort.

### Theory
- [ ] **1.T1 Hash tables** — *Grokking* ch.5 "Hash tables"; NeetCode Beginners: "Hash Usage", "Hash Implementation".
- [ ] **1.T2 Python dict/set internals and costs** — wiki.python.org/moin/TimeComplexity (dict, set); Python docs `collections` (`Counter`, `defaultdict`).
- [ ] **1.T3 Bucket sort** — NeetCode Beginners: "Bucket Sort".

### Problems

#### 1.1 Build a hash table from scratch (separate chaining) — Build — Hashing
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Implement a class `HashTable` without using `dict`/`set`:
`put(key, value)`, `get(key)` (raise `KeyError` if missing), `remove(key)`,
`__len__`, `__contains__`. Use a list of buckets; each bucket is a list of
`(key, value)` pairs. Resize (double the buckets and rehash) when the load
factor goes above 0.75. Example: `put("a", 1); put("a", 2); get("a")` → `2`.

**Must be able to explain:**
- [ ] What a collision is and how separate chaining handles it.
- [ ] Load factor, why resizing is needed and why it is amortized O(1).
- [ ] Worst-case complexity of `get` and when it happens.
- [ ] Why dictionary keys must be hashable (immutable) in Python.

#### 1.2 Ransom Note — Easy — Hashing  [LC 383](https://leetcode.com/problems/ransom-note/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Given strings `ransomNote` and `magazine`, return `True` if
`ransomNote` can be built using letters from `magazine`, each letter used at
most once. Example: `"aa", "aab"` → `True`; `"aa", "ab"` → `False`.

**Must be able to explain:**
- [ ] Frequency counting and its complexity.
- [ ] Why a fixed-size array of 26 counters is also O(1) space.

#### 1.3 Majority Element — Easy — Hashing  [LC 169](https://leetcode.com/problems/majority-element/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the element that appears more than `⌊n/2⌋` times (it
always exists). Example: `[2,2,1,1,1,2,2]` → `2`.

**Must be able to explain:**
- [ ] A hashing solution: time and space.
- [ ] A sorting solution: why it works and its complexity.
- [ ] (Stretch) That an O(1)-space approach exists (Boyer–Moore voting) and the intuition behind it.

#### 1.4 Contains Duplicate — Easy — Arrays & Hashing  [LC 217](https://leetcode.com/problems/contains-duplicate/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return `True` if any value appears at least twice in `nums`.
Example: `[1,2,3,1]` → `True`; `[1,2,3,4]` → `False`.

**Must be able to explain:**
- [ ] Brute force, sorting and hashing approaches with their complexities.
- [ ] Why `len(set(nums)) != len(nums)` is correct and what it costs.

#### 1.5 Valid Anagram — Easy — Hashing  [LC 242](https://leetcode.com/problems/valid-anagram/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return `True` if `t` is an anagram of `s` (same letters, same
counts). Example: `"anagram", "nagaram"` → `True`; `"rat", "car"` → `False`.

**Must be able to explain:**
- [ ] Sorting vs counting, with complexities.
- [ ] Early exit when lengths differ.
- [ ] What changes if inputs contain Unicode characters.

#### 1.6 Two Sum — Easy — Hashing  [LC 1](https://leetcode.com/problems/two-sum/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the indices of the two numbers in `nums` that add up to
`target`. Exactly one solution exists; an element cannot be used twice.
Example: `nums = [2,7,11,15], target = 9` → `[0,1]`.

**Must be able to explain:**
- [ ] The O(n²) brute force.
- [ ] The one-pass hashing idea and why it handles duplicates like `[3,3], target 6`.
- [ ] Time and space trade-off.

#### 1.7 Group Anagrams — Medium — Hashing  [LC 49](https://leetcode.com/problems/group-anagrams/)
- [x] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Group the strings that are anagrams of each other; any order.
Example: `["eat","tea","tan","ate","nat","bat"]` →
`[["bat"],["nat","tan"],["ate","eat","tea"]]`.

**Must be able to explain:**
- [ ] Two possible keys for a group and the complexity of each (n strings, max length k).
- [ ] Why a `list` cannot be a dict key but a `tuple` can.

#### 1.8 Top K Frequent Elements — Medium — Hashing / Bucket Sort or Heap  [LC 347](https://leetcode.com/problems/top-k-frequent-elements/)
- [x] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the `k` most frequent elements (any order). Better than
O(n log n) is expected. Example: `nums = [1,1,1,2,2,3], k = 2` → `[1,2]`.

**Must be able to explain:**
- [ ] The sort-by-frequency approach and its cost.
- [ ] The heap approach: O(n log k).
- [ ] The bucket-sort approach: why frequencies fit into `n + 1` buckets and why it is O(n).

#### 1.9 Encode and Decode Strings — Medium — Hashing / String  [LC 271](https://leetcode.com/problems/encode-and-decode-strings/) (premium — free at [neetcode.io](https://neetcode.io/problems/string-encode-and-decode))
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Design `encode(list[str]) -> str` and `decode(str) -> list[str]`
so that `decode(encode(x)) == x` for any list of strings, including strings
that contain any character (commas, digits, `#`, empty strings). Example:
`["neet","code","love","you"]` → some single string → back to the same list.

**Must be able to explain:**
- [ ] Why a simple delimiter breaks for some inputs (give a failing example).
- [ ] How your format makes decoding unambiguous.
- [ ] Complexity of encode and decode.

#### 1.10 Product of Array Except Self — Medium — Arrays (prefix/suffix)  [LC 238](https://leetcode.com/problems/product-of-array-except-self/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return `answer` where `answer[i]` is the product of all
elements except `nums[i]`, in O(n) time, **without division**. Example:
`[1,2,3,4]` → `[24,12,8,6]`.

**Must be able to explain:**
- [ ] Why division is a problem (zeros) even if it were allowed.
- [ ] How prefix products from Module 0 generalize here.
- [ ] How to get O(1) extra space (output array not counted).

#### 1.11 Valid Sudoku — Medium — Hashing  [LC 36](https://leetcode.com/problems/valid-sudoku/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Check whether a partially filled 9×9 board is valid: each row,
each column and each 3×3 box contains digits 1–9 without repetition (empty
cells are `"."`). You do not need to solve it. Example: a standard valid
partial board → `True`; one with two `8`s in the first column → `False`.

**Must be able to explain:**
- [ ] How to compute the box index of cell `(r, c)`.
- [ ] Why the complexity is effectively O(1) (fixed 81 cells) and O(n²) in general.

#### 1.12 Longest Consecutive Sequence — Medium — Hashing  [LC 128](https://leetcode.com/problems/longest-consecutive-sequence/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the length of the longest run of consecutive integers
in an unsorted array, in O(n) time. Example: `[100,4,200,1,3,2]` → `4`
(`1,2,3,4`).

**Must be able to explain:**
- [ ] The O(n log n) sorting approach.
- [ ] How to detect the start of a sequence in O(1).
- [ ] Why the total work is O(n) even though there is a loop inside a loop.

### Module checklist — I can…
- [ ] Implement a hash table with separate chaining and resizing from a blank file.
- [ ] Explain collisions, load factor, and average vs worst-case lookup.
- [ ] Choose between `dict`, `set`, `Counter`, `defaultdict` for a task.
- [ ] Recognise "have I seen this before?" / "count things" problems as hashing problems.
- [ ] Explain bucket sort and when it beats comparison sorting.

**Estimated hours:** ~16h

### Self-check interview questions
1. How does a hash table achieve average O(1) lookup?
2. What is a collision? Name two strategies to resolve collisions.
3. What is the load factor, and what happens when it gets too high?
4. Why must dict keys in Python be hashable? Can a tuple containing a list be a key?
5. What is the worst-case time of a dict lookup, and when does it happen?
6. When is sorting a better choice than hashing?
7. Why can bucket sort be O(n)?

---

**Answers**
1. A hash function maps the key to a bucket index; with a good hash function and a bounded load factor, each bucket holds O(1) items on average.
2. Two different keys map to the same bucket. Separate chaining (list per bucket) and open addressing (probe for another free slot — CPython's dict uses open addressing).
3. Items ÷ buckets. When it is high, buckets get crowded and lookups slow down, so the table resizes (allocates more buckets and rehashes everything).
4. The hash must stay the same for the key's lifetime; mutable objects could change and be "lost" in the wrong bucket. No — a tuple containing a list is unhashable.
5. O(n), when many keys collide into the same bucket/probe sequence (bad hash function or adversarial input).
6. When you need order (ranges, k-th smallest), when memory is tight, or when you need a deterministic O(n log n) bound without extra space.
7. It does not compare elements; it places them directly by value/frequency into a bounded number of buckets, so it is linear when the value range is small.

---

## Module 2 — Two Pointers (~10h)

**Topics:** two pointers moving towards each other on sorted input, fast/slow
pointers in the same direction (read/write pointers for in-place edits),
reducing k-Sum to (k−1)-Sum, skipping duplicates, proving a pointer move is
safe.

### Theory
- [ ] **2.T1 Two pointers** — NeetCode Advanced Algorithms: "Two Pointers".
- [ ] **2.T2 Why sorting enables two pointers** — re-watch NeetCode video for "Two Sum II" after attempting it; *Grokking* ch.1 (sorted input intuition from binary search).

### Problems

#### 2.1 Merge Sorted Array — Easy — Two Pointers  [LC 88](https://leetcode.com/problems/merge-sorted-array/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** `nums1` has length `m + n`: the first `m` elements are sorted
values, the last `n` are zeros. `nums2` has `n` sorted values. Merge `nums2`
into `nums1` in place so `nums1` is sorted. Example:
`nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3` → `[1,2,2,3,5,6]`.

**Must be able to explain:**
- [ ] Why filling from the front forces extra copying.
- [ ] What happens when one array is exhausted first.
- [ ] Time and space complexity.

#### 2.2 Move Zeroes — Easy — Two Pointers (read/write)  [LC 283](https://leetcode.com/problems/move-zeroes/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Move all `0`s to the end of the array in place, keeping the
relative order of non-zero elements. Example: `[0,1,0,3,12]` → `[1,3,12,0,0]`.

**Must be able to explain:**
- [ ] The role of each pointer and the invariant between them.
- [ ] Why the solution is O(n) time, O(1) space.

#### 2.3 Squares of a Sorted Array — Easy — Two Pointers  [LC 977](https://leetcode.com/problems/squares-of-a-sorted-array/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Given a sorted array (may contain negatives), return the sorted
array of squares in O(n). Example: `[-4,-1,0,3,10]` → `[0,1,9,16,100]`.

**Must be able to explain:**
- [ ] Why "square then sort" is O(n log n).
- [ ] Where the largest square can be, and how that leads to O(n).

#### 2.4 Valid Palindrome — Easy — Two Pointers  [LC 125](https://leetcode.com/problems/valid-palindrome/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** After lower-casing and removing all non-alphanumeric
characters, is the string a palindrome? Example:
`"A man, a plan, a canal: Panama"` → `True`; `"race a car"` → `False`.

**Must be able to explain:**
- [ ] The build-a-cleaned-copy approach vs the O(1)-space approach.
- [ ] Edge cases: empty string, string with only punctuation.
- [ ] `str.isalnum()` and what counts as alphanumeric.

#### 2.5 Two Sum II – Input Array Is Sorted — Medium — Two Pointers  [LC 167](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** `numbers` is sorted ascending (1-indexed). Return `[i, j]`
with `numbers[i] + numbers[j] == target`, using O(1) extra space. Exactly one
solution exists. Example: `[2,7,11,15], target 9` → `[1,2]`.

**Must be able to explain:**
- [ ] Why the hash-map solution from Two Sum violates the space requirement.
- [ ] Why moving a pointer never skips the answer (the correctness argument).

#### 2.6 3Sum — Medium — Two Pointers  [LC 15](https://leetcode.com/problems/3sum/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return all **unique** triplets `[a, b, c]` from `nums` with
`a + b + c == 0` (no duplicate triplets in the output). Example:
`[-1,0,1,2,-1,-4]` → `[[-1,-1,2],[-1,0,1]]`.

**Must be able to explain:**
- [ ] The O(n³) brute force and why it produces duplicates.
- [ ] How this reduces to a problem you already solved.
- [ ] Every place duplicates must be skipped.
- [ ] Final time and space complexity.

#### 2.7 Container With Most Water — Medium — Two Pointers  [LC 11](https://leetcode.com/problems/container-with-most-water/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** `height[i]` is the height of a vertical line at `x = i`. Choose
two lines that, with the x-axis, hold the most water; return that area.
Example: `[1,8,6,2,5,4,8,3,7]` → `49`.

**Must be able to explain:**
- [ ] The area formula.
- [ ] Which pointer to move and the argument for why the other choice can never help.

#### 2.8 Trapping Rain Water — Hard — Two Pointers — **OPTIONAL**  [LC 42](https://leetcode.com/problems/trapping-rain-water/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Given bar heights (width 1), compute how much rain water is
trapped after raining. Example: `[0,1,0,2,1,0,1,3,2,1,2,1]` → `6`.

**Must be able to explain:**
- [ ] The water above one bar in terms of the tallest bars on its left and right.
- [ ] An O(n)-space prefix/suffix approach.
- [ ] How the O(1)-space version decides which side to process.

### Module checklist — I can…
- [ ] Recognise when sorted input (or sorting first) enables two pointers.
- [ ] Use a read/write pointer pair for in-place array edits.
- [ ] Argue why a pointer move is safe (does not skip the answer).
- [ ] Remove duplicates from k-Sum results without a set.

**Estimated hours:** ~10h

### Self-check interview questions
1. When is two pointers applicable, and what does it usually replace?
2. What is the difference between opposite-direction and same-direction two pointers?
3. Why does 3Sum sort the array first? What does sorting cost relative to the rest?
4. How would you generalise 3Sum to 4Sum, and what is the complexity?
5. How can you do in-place edits of an array in O(1) extra space?

---

**Answers**
1. On sorted arrays/strings or linked structures where you compare or combine elements from two positions; it usually replaces an O(n²) nested loop with O(n).
2. Opposite-direction pointers start at both ends and move inward (pair sums, palindromes). Same-direction pointers move forward together at different speeds (read/write compaction, fast/slow).
3. Sorting makes the two-pointer inner step possible and makes duplicates adjacent so they are easy to skip. O(n log n) sort is dominated by the O(n²) main loop.
4. Fix two elements with nested loops, then run two pointers on the rest: O(n³). In general k-Sum is O(n^(k−1)).
5. Keep a write pointer marking where the next kept element goes, and a read pointer scanning every element; copy only elements that should stay.

---

## Module 3 — Sliding Window (~12h)

**Topics:** fixed-size windows, variable-size windows (expand right, shrink
left while invalid), maintaining window state (counts, sums, a set,
"max frequency"), when a window must be monotonic, deque for window maximum.

### Theory
- [ ] **3.T1 Fixed-size sliding window** — NeetCode Advanced Algorithms: "Sliding Window Fixed Size".
- [ ] **3.T2 Variable-size sliding window** — NeetCode Advanced Algorithms: "Sliding Window Variable Size".
- [ ] **3.T3 `collections.deque`** — Python docs `collections.deque` (O(1) at both ends).

### Problems

#### 3.1 Contains Duplicate II — Easy — Sliding Window  [LC 219](https://leetcode.com/problems/contains-duplicate-ii/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return `True` if there are two indices `i != j` with
`nums[i] == nums[j]` and `abs(i - j) <= k`. Example:
`nums = [1,2,3,1], k = 3` → `True`; `nums = [1,2,3,1,2,3], k = 2` → `False`.

**Must be able to explain:**
- [ ] What the window represents and when it must shrink.
- [ ] Time and space complexity in terms of n and k.

#### 3.2 Maximum Average Subarray I — Easy — Sliding Window (fixed)  [LC 643](https://leetcode.com/problems/maximum-average-subarray-i/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Find the contiguous subarray of length `k` with the maximum
average and return that average. Example: `nums = [1,12,-5,-6,50,3], k = 4`
→ `12.75`.

**Must be able to explain:**
- [ ] Why recomputing each window sum is O(n·k).
- [ ] How the window sum is updated in O(1) per step.

#### 3.3 Best Time to Buy and Sell Stock — Easy — Sliding Window  [LC 121](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** `prices[i]` is the stock price on day `i`. Buy once and sell
once later; return the max profit (0 if no profit). Example:
`[7,1,5,3,6,4]` → `5`.

**Must be able to explain:**
- [ ] The O(n²) brute force.
- [ ] What the "left" and "right" of the window mean and when left moves.

#### 3.4 Longest Substring Without Repeating Characters — Medium — Sliding Window  [LC 3](https://leetcode.com/problems/longest-substring-without-repeating-characters/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the length of the longest substring with no repeated
characters. Example: `"abcabcbb"` → `3` (`"abc"`); `"bbbbb"` → `1`.

**Must be able to explain:**
- [ ] What makes the window invalid and how you restore validity.
- [ ] Why each character enters and leaves the window at most once → O(n).
- [ ] Edge cases: empty string, all same characters.

#### 3.5 Longest Repeating Character Replacement — Medium — Sliding Window  [LC 424](https://leetcode.com/problems/longest-repeating-character-replacement/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** You may replace at most `k` characters of an uppercase string
with any letter. Return the length of the longest substring of one repeated
letter you can get. Example: `s = "AABABBA", k = 1` → `4`.

**Must be able to explain:**
- [ ] The validity condition of a window in terms of its length, its most frequent character count, and `k`.
- [ ] Why the complexity is O(26·n) or O(n).
- [ ] (Stretch) Why the "max frequency" does not need to be decreased when shrinking.

#### 3.6 Permutation in String — Medium — Sliding Window  [LC 567](https://leetcode.com/problems/permutation-in-string/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return `True` if `s2` contains a permutation of `s1` as a
substring. Example: `s1 = "ab", s2 = "eidbaooo"` → `True` (`"ba"`);
`s1 = "ab", s2 = "eidboaoo"` → `False`.

**Must be able to explain:**
- [ ] Why the window size is fixed here.
- [ ] How two frequency arrays are compared cheaply as the window slides.

#### 3.7 Minimum Window Substring — Hard — Sliding Window — **OPTIONAL**  [LC 76](https://leetcode.com/problems/minimum-window-substring/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the shortest substring of `s` containing every
character of `t` (including duplicates); `""` if none. Example:
`s = "ADOBECODEBANC", t = "ABC"` → `"BANC"`.

**Must be able to explain:**
- [ ] How you know in O(1) that the window currently covers `t`.
- [ ] When to expand, when to shrink, and when to record the answer.
- [ ] Time complexity in terms of `len(s)` and `len(t)`.

#### 3.8 Sliding Window Maximum — Hard — Sliding Window / Monotonic Deque — **OPTIONAL**  [LC 239](https://leetcode.com/problems/sliding-window-maximum/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** For every window of size `k` moving left to right, return the
maximum. Example: `nums = [1,3,-1,-3,5,3,6,7], k = 3` → `[3,3,5,5,6,7]`.

**Must be able to explain:**
- [ ] The O(n·k) brute force and an O(n log k) heap approach.
- [ ] What invariant the deque keeps and why that gives O(n).

### Module checklist — I can…
- [ ] Tell fixed-size from variable-size window problems.
- [ ] Write the expand-right / shrink-left template from a blank file.
- [ ] Maintain window state (counts, sum, set) in O(1) per step.
- [ ] Explain why a sliding window is O(n) despite the nested loop.

**Estimated hours:** ~12h

### Self-check interview questions
1. What kind of problems does a sliding window solve?
2. Why is a variable-size window O(n) even though it has a `while` inside a `for`?
3. When does a sliding window not work (hint: negative numbers and sums)?
4. What is the difference between a sliding window and two pointers?
5. What is a monotonic deque and what does it give you?

---

**Answers**
1. Problems about contiguous subarrays/substrings where you optimise a length or a value subject to a condition that can be checked incrementally.
2. The left pointer only moves forward, so across the whole run each element is added once and removed once: 2n steps total.
3. When shrinking the window does not reliably make it "more valid" — e.g. subarray sum equals k with negative numbers; then prefix sums + hashing are used instead.
4. A sliding window is a special case of same-direction two pointers where the elements between the pointers (the window) and their aggregate state matter.
5. A deque kept in increasing or decreasing order, so the front is always the window's min or max; each element is pushed and popped once → O(n) overall.

---

## Module 4 — Stack (~12h)

**Topics:** LIFO, stack via Python list, matching/nesting problems, stack as
"undo"/history, expression evaluation, monotonic stack (next greater /
smaller element), stacks of pairs (value + extra info).

### Theory
- [ ] **4.T1 Stacks** — NeetCode Beginners: "Stacks"; *Grokking* ch.3 "Recursion" (the call stack section).
- [ ] **4.T2 Monotonic stack** — NeetCode video for "Daily Temperatures" (watch after your attempt).

### Problems

#### 4.1 Build a stack from scratch (array-backed and linked-list-backed) — Build — Stack
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Implement two classes with the same interface — `push(x)`,
`pop()` (raise `IndexError` when empty), `peek()`, `is_empty()`,
`__len__`: `ArrayStack` using a Python list, and `LinkedStack` using your
own `Node` class (no list). Example: `push(1); push(2); pop()` → `2`,
`peek()` → `1`.

**Must be able to explain:**
- [ ] The complexity of every operation in both versions.
- [ ] Why the list version pushes/pops at the end, not the front.
- [ ] Memory trade-offs of the two versions.

#### 4.2 Baseball Game — Easy — Stack  [LC 682](https://leetcode.com/problems/baseball-game/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Process operations: an integer (record it), `"+"` (sum of the
previous two), `"D"` (double the previous), `"C"` (remove the previous).
Return the sum of all records. Example: `["5","2","C","D","+"]` → `30`.

**Must be able to explain:**
- [ ] Why a stack models "previous" and "undo" naturally.
- [ ] Time and space complexity.

#### 4.3 Valid Parentheses — Easy — Stack  [LC 20](https://leetcode.com/problems/valid-parentheses/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** A string contains only `()[]{}`. Return `True` if every bracket
is closed by the same type in the correct order. Example: `"()[]{}"` →
`True`; `"(]"` → `False`; `"([)]"` → `False`.

**Must be able to explain:**
- [ ] Why a simple counter works for one bracket type but not for three.
- [ ] The two ways the string can be invalid at the end or in the middle.

#### 4.4 Min Stack — Medium — Stack  [LC 155](https://leetcode.com/problems/min-stack/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Design a stack with `push`, `pop`, `top` and `getMin`, all
O(1). Example: `push(-2), push(0), push(-3), getMin()` → `-3`; `pop()`,
`getMin()` → `-2`.

**Must be able to explain:**
- [ ] Why a single `min` variable breaks after `pop`.
- [ ] What extra information you store and the space cost.

#### 4.5 Evaluate Reverse Polish Notation — Medium — Stack  [LC 150](https://leetcode.com/problems/evaluate-reverse-polish-notation/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Evaluate an expression in postfix notation with `+ - * /`
(division truncates toward zero). Example: `["2","1","+","3","*"]` → `9`;
`["4","13","5","/","+"]` → `6`.

**Must be able to explain:**
- [ ] Operand order for `-` and `/`.
- [ ] Why `//` in Python is wrong for negative numbers here and what to use instead.

#### 4.6 Generate Parentheses — Medium — Backtracking / Stack  [LC 22](https://leetcode.com/problems/generate-parentheses/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Generate all well-formed combinations of `n` pairs of
parentheses. Example: `n = 3` → `["((()))","(()())","(())()","()(())","()()()"]`.

**Must be able to explain:**
- [ ] The two rules deciding when you may add `(` and when you may add `)`.
- [ ] How the recursion tree looks for `n = 2`.
- [ ] Why the output size (Catalan numbers) dominates the complexity.

#### 4.7 Daily Temperatures — Medium — Monotonic Stack  [LC 739](https://leetcode.com/problems/daily-temperatures/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** For each day, return how many days you wait for a warmer
temperature (0 if never). Example: `[73,74,75,71,69,72,76,73]` →
`[1,1,4,2,1,1,0,0]`.

**Must be able to explain:**
- [ ] The O(n²) brute force.
- [ ] What the stack stores (values or indices?) and its ordering invariant.
- [ ] Why each index is pushed and popped at most once → O(n).

#### 4.8 Car Fleet — Medium — Monotonic Stack  [LC 853](https://leetcode.com/problems/car-fleet/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** `n` cars drive to `target` on a one-lane road; `position[i]`
and `speed[i]` are given. A faster car that catches a slower one forms a
fleet and moves at the slower speed. Return the number of fleets arriving.
Example: `target = 12, position = [10,8,0,5,3], speed = [2,4,1,1,3]` → `3`.

**Must be able to explain:**
- [ ] Why sorting by position is the first step.
- [ ] What quantity per car decides whether it joins the fleet ahead.
- [ ] Time complexity.

#### 4.9 Largest Rectangle in Histogram — Hard — Monotonic Stack — **OPTIONAL**  [LC 84](https://leetcode.com/problems/largest-rectangle-in-histogram/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Bars of width 1 with heights `heights[i]`. Return the area of
the largest rectangle in the histogram. Example: `[2,1,5,6,2,3]` → `10`.

**Must be able to explain:**
- [ ] For a given bar used as the rectangle height, how far it can extend left and right.
- [ ] What a popped bar tells you and what width it gets.
- [ ] How remaining bars are handled at the end.

### Module checklist — I can…
- [ ] Implement a stack both with a list and with linked nodes.
- [ ] Recognise matching/nesting problems as stack problems.
- [ ] Explain and code a monotonic stack for "next greater element" questions.
- [ ] Explain why monotonic-stack solutions are O(n).

**Estimated hours:** ~12h

### Self-check interview questions
1. What is LIFO? Give two real-world uses of a stack in software.
2. Why should a Python list-based stack push/pop at the end?
3. How does the call stack relate to recursion? Can any recursion be rewritten with an explicit stack?
4. What is a monotonic stack?
5. How would you implement a queue using two stacks, and what is the amortized cost?

---

**Answers**
1. Last In, First Out. Function call stack, undo history, expression parsing, browser back button, DFS.
2. `append`/`pop()` at the end are amortized O(1); inserting/removing at index 0 shifts every element (O(n)).
3. Each call pushes a frame with local state; returning pops it. Yes — you can simulate recursion by pushing the state you would pass to the recursive call onto your own stack.
4. A stack whose elements are kept in increasing (or decreasing) order; before pushing, you pop elements that would break the order. Used for next greater/smaller element problems.
5. Push into an "in" stack; pop from an "out" stack, refilling "out" from "in" only when "out" is empty. Each element moves at most once → amortized O(1) per operation.

---

## Module 5 — Binary Search (~13h)

**Topics:** classic binary search, the `lo`/`hi`/`mid` template and its
off-by-one traps, searching for a boundary (first/last position, insert
point), binary search on a rotated array, **binary search on the answer**
(search over possible results instead of indices), 2-D matrices as 1-D
arrays, Python's `bisect` module.

### Theory
- [ ] **5.T1 Binary search on arrays** — NeetCode Beginners: "Search Array"; *Grokking* ch.1 (binary search).
- [ ] **5.T2 Binary search on a range (on the answer)** — NeetCode Beginners: "Search Range".
- [ ] **5.T3 `bisect` module** — Python docs `bisect` (`bisect_left`, `bisect_right`).

### Problems

#### 5.1 Guess Number Higher or Lower — Easy — Binary Search  [LC 374](https://leetcode.com/problems/guess-number-higher-or-lower/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** A number was picked from `1..n`. An API `guess(num)` returns
`-1` if your guess is too high, `1` if too low, `0` if correct. Find the
number. Example: `n = 10, pick = 6` → `6`. (Write your own `guess` stub in
`tests()`.)

**Must be able to explain:**
- [ ] The maximum number of `guess` calls for `n = 1_000_000`.
- [ ] Why `mid = (lo + hi) // 2` is fine in Python but overflows in Java/C (and the safe form).

#### 5.2 Sqrt(x) — Easy — Binary Search on the Answer  [LC 69](https://leetcode.com/problems/sqrtx/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return `⌊√x⌋` for a non-negative integer `x` without `**0.5`
or `math.sqrt`. Example: `x = 8` → `2`; `x = 16` → `4`.

**Must be able to explain:**
- [ ] What the search space is here (not an array!).
- [ ] Which value to return when the loop ends and why.

#### 5.3 Binary Search — Easy — Binary Search  [LC 704](https://leetcode.com/problems/binary-search/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the index of `target` in a sorted array, or `-1`, in
O(log n). Example: `nums = [-1,0,3,5,9,12], target = 9` → `4`.

**Must be able to explain:**
- [ ] Your loop invariant: what is guaranteed about `lo` and `hi` in every iteration.
- [ ] Iterative vs recursive version: space complexity of each.

#### 5.4 Search a 2D Matrix — Medium — Binary Search  [LC 74](https://leetcode.com/problems/search-a-2d-matrix/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Each row is sorted and each row's first value is greater than
the previous row's last value. Return whether `target` exists, in
O(log(m·n)). Example: `[[1,3,5,7],[10,11,16,20],[23,30,34,60]], target 3` → `True`.

**Must be able to explain:**
- [ ] How a 1-D index maps to `(row, col)` and back.
- [ ] Alternative: two binary searches (row, then column) and its complexity.

#### 5.5 Koko Eating Bananas — Medium — Binary Search on the Answer  [LC 875](https://leetcode.com/problems/koko-eating-bananas/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** `piles[i]` bananas; each hour Koko picks one pile and eats up
to `k` bananas from it. Return the minimum integer `k` so she finishes
within `h` hours. Example: `piles = [3,6,7,11], h = 8` → `4`.

**Must be able to explain:**
- [ ] The lowest and highest possible `k`.
- [ ] Why "can finish with speed k" is monotonic in `k` — the property that allows binary search.
- [ ] Total complexity in terms of `n` and `max(piles)`.

#### 5.6 Find Minimum in Rotated Sorted Array — Medium — Binary Search  [LC 153](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** A sorted array of unique values was rotated between 1 and n
times. Return its minimum in O(log n). Example: `[3,4,5,1,2]` → `1`;
`[11,13,15,17]` → `11`.

**Must be able to explain:**
- [ ] How comparing `mid` with one end tells you which half is sorted.
- [ ] The not-rotated case.

#### 5.7 Search in Rotated Sorted Array — Medium — Binary Search  [LC 33](https://leetcode.com/problems/search-in-rotated-sorted-array/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Search `target` in a rotated sorted array of unique values in
O(log n); return its index or `-1`. Example:
`nums = [4,5,6,7,0,1,2], target = 0` → `4`.

**Must be able to explain:**
- [ ] How you decide which half to keep after finding the sorted half.
- [ ] Why duplicates (LC 81) break the O(log n) guarantee.

#### 5.8 Time Based Key-Value Store — Medium — Binary Search  [LC 981](https://leetcode.com/problems/time-based-key-value-store/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Design `TimeMap` with `set(key, value, timestamp)` and
`get(key, timestamp)` returning the value set with the largest
`timestamp_prev <= timestamp`, or `""`. Timestamps for `set` are strictly
increasing. Example: `set("foo","bar",1); get("foo",3)` → `"bar"`;
`set("foo","bar2",4); get("foo",4)` → `"bar2"`; `get("foo",0)` → `""`.

**Must be able to explain:**
- [ ] Why the per-key lists stay sorted without sorting.
- [ ] Complexity of `set` and `get`.
- [ ] Which `bisect` function matches "largest ≤ timestamp".

#### 5.9 Median of Two Sorted Arrays — Hard — Binary Search — **OPTIONAL**  [LC 4](https://leetcode.com/problems/median-of-two-sorted-arrays/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the median of two sorted arrays in O(log(m + n)).
Example: `[1,3], [2]` → `2.0`; `[1,2], [3,4]` → `2.5`.

**Must be able to explain:**
- [ ] The O(m + n) merge approach first.
- [ ] What a "partition" of both arrays means and when it is correct.
- [ ] Why you binary-search the shorter array.

### Module checklist — I can…
- [ ] Write a bug-free binary search from a blank file and state its invariant.
- [ ] Find a boundary (first ≥ target) with `bisect_left` and by hand.
- [ ] Recognise "minimum k such that condition(k) holds" as binary search on the answer.
- [ ] Handle rotated arrays by identifying the sorted half.

**Estimated hours:** ~13h

### Self-check interview questions
1. What property must a problem have for binary search to apply?
2. What is binary search on the answer? Give an example.
3. What is the difference between `bisect_left` and `bisect_right`?
4. Why can `(lo + hi) / 2` overflow in some languages, and how do you avoid it?
5. How many iterations does binary search need for 1 billion elements?
6. Iterative vs recursive binary search: which do you prefer and why?

---

**Answers**
1. A monotonic predicate: for some ordering, the condition is false then true (or vice versa) with a single switch point — sorted arrays are the classic case.
2. Instead of searching indices, you search a range of candidate answers and test each candidate with a feasibility check, e.g. the minimum eating speed in Koko Eating Bananas.
3. For a value already present, `bisect_left` returns the index of its first occurrence (insert before equals); `bisect_right` returns the index after its last occurrence.
4. With fixed-width integers `lo + hi` can exceed the maximum int. Use `lo + (hi - lo) // 2`. Python ints are arbitrary precision, so it's not an issue there.
5. About 30 (2³⁰ ≈ 1.07 billion).
6. Iterative: O(1) space and no recursion-depth limit; recursive is fine to explain but uses O(log n) stack.

---

## Module 6 — Linked List (~18h)

**Topics:** singly and doubly linked lists, `Node` classes, dummy/sentinel
head, reversing pointers, fast/slow pointers (middle, cycle detection —
Floyd's algorithm), merging lists, hash map + linked list combos (LRU), in-place
vs extra-space trade-offs.

### Theory
- [ ] **6.T1 Singly linked lists** — NeetCode Beginners: "Singly Linked Lists"; *Grokking* ch.2 (arrays vs linked lists).
- [ ] **6.T2 Doubly linked lists** — NeetCode Beginners: "Doubly Linked Lists".
- [ ] **6.T3 Fast and slow pointers** — NeetCode Advanced Algorithms: "Fast and Slow Pointers".
- [ ] **6.T4 `OrderedDict`** — Python docs `collections.OrderedDict` (`move_to_end`, `popitem(last=False)`), to compare with your own LRU.

### Problems

#### 6.1 Build a singly linked list from scratch — Build — Linked List
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Implement `LinkedList` with your own `Node` class:
`append(x)`, `prepend(x)`, `insert(index, x)`, `remove(x)` (first
occurrence, raise `ValueError` if missing), `find(x) -> bool`, `__len__`,
`__iter__` (yield values) and `__repr__` like `1 -> 2 -> 3`. Example:
`append(1); append(3); insert(1, 2); list(ll)` → `[1, 2, 3]`.

**Must be able to explain:**
- [ ] The complexity of each method, and how a `tail` pointer changes `append`.
- [ ] Why a dummy head simplifies insert/remove at the front.
- [ ] Linked list vs Python list: when each wins.

#### 6.2 Middle of the Linked List — Easy — Fast & Slow Pointers  [LC 876](https://leetcode.com/problems/middle-of-the-linked-list/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the middle node; if there are two middle nodes, return
the second. Example: `1→2→3→4→5` → node `3`; `1→2→3→4→5→6` → node `4`.

**Must be able to explain:**
- [ ] The two-pass (count then walk) approach.
- [ ] Why one pass with two speeds works, and the loop condition.

#### 6.3 Reverse Linked List — Easy — Linked List  [LC 206](https://leetcode.com/problems/reverse-linked-list/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Reverse a singly linked list and return the new head. Example:
`1→2→3→4→5` → `5→4→3→2→1`. Do it both iteratively and recursively.

**Must be able to explain:**
- [ ] Which pointers you need at each step and in what order you update them.
- [ ] Space complexity of the iterative vs recursive version.

#### 6.4 Merge Two Sorted Lists — Easy — Linked List  [LC 21](https://leetcode.com/problems/merge-two-sorted-lists/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Merge two sorted lists by splicing their nodes; return the
head. Example: `1→2→4`, `1→3→4` → `1→1→2→3→4→4`.

**Must be able to explain:**
- [ ] How a dummy node avoids special-casing the head.
- [ ] What to do with the leftover list.
- [ ] Relation to the merge step of merge sort (Module 0).

#### 6.5 Linked List Cycle — Easy — Fast & Slow Pointers (Floyd's)  [LC 141](https://leetcode.com/problems/linked-list-cycle/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return `True` if the list has a cycle. Example: `3→2→0→-4`
with `-4` pointing back to `2` → `True`.

**Must be able to explain:**
- [ ] The hash-set approach and its space cost.
- [ ] Why the fast pointer must meet the slow one inside a cycle.

#### 6.6 Reorder List — Medium — Linked List  [LC 143](https://leetcode.com/problems/reorder-list/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Reorder `L0→L1→…→Ln` into `L0→Ln→L1→Ln-1→…` in place (change
links, not values). Example: `1→2→3→4` → `1→4→2→3`; `1→2→3→4→5` → `1→5→2→4→3`.

**Must be able to explain:**
- [ ] How this combines three simpler problems from this module.
- [ ] The O(n)-space approach vs the O(1)-space approach.

#### 6.7 Remove Nth Node From End of List — Medium — Linked List / Two Pointers  [LC 19](https://leetcode.com/problems/remove-nth-node-from-end-of-list/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Remove the `n`-th node from the end and return the head, in one
pass if possible. Example: `1→2→3→4→5, n = 2` → `1→2→3→5`; `[1], n = 1` → `[]`.

**Must be able to explain:**
- [ ] The two-pass approach.
- [ ] The gap between the two pointers and why it gives one pass.
- [ ] Why a dummy node matters when the head itself is removed.

#### 6.8 Copy List with Random Pointer — Medium — Linked List / Hashing  [LC 138](https://leetcode.com/problems/copy-list-with-random-pointer/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Each node has `next` and `random` (any node or `None`).
Return a **deep copy**: new nodes only, with the same structure. Example:
`[[7,null],[13,0],[11,4],[10,2],[1,0]]` (value, random index) → an
identical-looking but fully separate list.

**Must be able to explain:**
- [ ] Why a single pass cannot set `random` directly.
- [ ] The role of an old-node → new-node map.
- [ ] (Stretch) The O(1)-extra-space interleaving idea.

#### 6.9 Add Two Numbers — Medium — Linked List  [LC 2](https://leetcode.com/problems/add-two-numbers/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Two non-negative integers are stored as linked lists of digits
in **reverse** order. Return their sum as a linked list in the same format.
Example: `2→4→3` + `5→6→4` → `7→0→8` (342 + 465 = 807).

**Must be able to explain:**
- [ ] Handling different lengths and the final carry.
- [ ] Why converting to `int` and back is not the intended solution (and when it would fail in other languages).

#### 6.10 Find the Duplicate Number — Medium — Fast & Slow Pointers  [LC 287](https://leetcode.com/problems/find-the-duplicate-number/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** `nums` has `n + 1` integers in `1..n`; exactly one value is
repeated (possibly many times). Find it **without modifying** `nums` and
with O(1) extra space. Example: `[1,3,4,2,2]` → `2`; `[3,1,3,4,2]` → `3`.

**Must be able to explain:**
- [ ] Why the constraints rule out sorting and a set.
- [ ] How the array can be seen as a linked list (index → value).
- [ ] The two phases of Floyd's algorithm and what each finds.

#### 6.11 LRU Cache — Medium — Linked List + Hash Map  [LC 146](https://leetcode.com/problems/lru-cache/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Design `LRUCache(capacity)` with `get(key)` (return `-1` if
missing) and `put(key, value)`, both O(1). When full, evict the least
recently used key. Example: capacity 2: `put(1,1), put(2,2), get(1)` → `1`;
`put(3,3)` evicts key 2; `get(2)` → `-1`.

**Must be able to explain:**
- [ ] Why a dict alone or a list alone cannot give O(1) for both operations.
- [ ] What the doubly linked list orders and what the dict maps to.
- [ ] Why sentinel head/tail nodes remove edge cases.
- [ ] How `OrderedDict` would do it (and why interviewers usually want your own list).

#### 6.12 Merge k Sorted Lists — Hard — Heap / Divide & Conquer — **OPTIONAL**  [LC 23](https://leetcode.com/problems/merge-k-sorted-lists/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Merge `k` sorted linked lists into one sorted list. Example:
`[1→4→5, 1→3→4, 2→6]` → `1→1→2→3→4→4→5→6`.

**Must be able to explain:**
- [ ] Merging one by one: why it is O(k·N).
- [ ] Pairwise (divide & conquer) merging: O(N log k).
- [ ] The heap approach (after Module 9) and the tie-breaking issue in Python's `heapq` with nodes.

#### 6.13 Reverse Nodes in k-Group — Hard — Linked List — **OPTIONAL**  [LC 25](https://leetcode.com/problems/reverse-nodes-in-k-group/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Reverse the nodes of the list `k` at a time; a final group
shorter than `k` stays as is. Example: `1→2→3→4→5, k = 2` → `2→1→4→3→5`;
`k = 3` → `3→2→1→4→5`.

**Must be able to explain:**
- [ ] How you check that a full group of `k` exists before reversing.
- [ ] Which four pointers connect a reversed group to the rest.

#### 6.14 LFU Cache — Hard — Design / Hashing — **OPTIONAL**  [LC 460](https://leetcode.com/problems/lfu-cache/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Design `LFUCache(capacity)` with O(1) `get` and `put`. When
full, evict the key with the lowest use count; ties go to the least recently
used among them. Example: capacity 2: `put(1,1), put(2,2), get(1)` → `1`;
`put(3,3)` evicts key 2 (count 1 vs key 1's count 2).

**Must be able to explain:**
- [ ] What structure groups keys by frequency, and how you find the minimum frequency in O(1).
- [ ] How it differs from LRU and where LFU is used in practice.

### Module checklist — I can…
- [ ] Implement a singly linked list with a dummy head from a blank file.
- [ ] Reverse a list iteratively and recursively without drawing it first.
- [ ] Use fast/slow pointers for the middle, cycle detection and cycle start.
- [ ] Design an LRU cache with a hash map + doubly linked list.
- [ ] Explain linked list vs array trade-offs (access, insert, cache locality).

**Estimated hours:** ~18h

### Self-check interview questions
1. Compare arrays and linked lists for access, insertion at the front, insertion in the middle and memory use.
2. What is a sentinel (dummy) node and why is it useful?
3. How does Floyd's cycle detection work, and how do you find where the cycle starts?
4. Why does LRU need both a hash map and a doubly linked list?
5. Why are linked lists often slower than arrays in practice even with the same Big O?
6. How is Python's `collections.deque` implemented, roughly?

---

**Answers**
1. Array: O(1) index access, O(n) insert at front/middle (shifting), compact memory. Linked list: O(n) access, O(1) insert at front (or after a known node), extra memory per node for pointers.
2. A placeholder node before the real head (and/or after the tail) so that inserting or deleting at the ends uses the same code as in the middle — no special cases for an empty list or a changing head.
3. Slow moves 1 step, fast moves 2; if there is a cycle they must meet inside it. Then reset one pointer to the head and move both 1 step at a time — they meet at the cycle start.
4. The hash map finds a node by key in O(1); the doubly linked list keeps usage order and lets you move/remove any node in O(1) given a pointer to it.
5. Nodes are scattered in memory, so traversal causes cache misses; arrays are contiguous and CPU-cache friendly. Each node also has allocation and pointer overhead.
6. As a doubly linked list of fixed-size blocks (arrays), giving O(1) appends and pops at both ends.

---

## Module 7 — Trees (~25h)

**Topics:** tree vocabulary (root, leaf, height, depth), binary trees, the
three DFS traversals (pre-, in-, post-order) recursively and with an
explicit stack, BFS / level-order traversal with a queue, binary search
trees (search, insert, delete, in-order = sorted), balanced vs unbalanced
trees, returning information from subtrees (height, validity, max path),
building a tree from traversals, serialisation.

### Theory
- [ ] **7.T1 Queues (BFS prep)** — NeetCode Beginners: "Queues"; *Grokking* ch.6 "Breadth-first search" (queue part only).
- [ ] **7.T2 Binary trees** — NeetCode Beginners: "Binary Tree"; *Grokking* ch.7 "Trees".
- [ ] **7.T3 Depth-first search** — NeetCode Beginners: "Depth-First Search" (in-/pre-/post-order).
- [ ] **7.T4 Breadth-first search** — NeetCode Beginners: "Breadth-First Search".
- [ ] **7.T5 Binary search trees** — NeetCode Beginners: "Binary Search Tree", "BST Insert and Remove", "BST Sets and Maps".
- [ ] **7.T6 Balanced trees (reading)** — *Grokking* ch.8 "Balanced trees" (AVL intuition; why balance keeps operations O(log n)).

### Problems

#### 7.1 Build a queue from scratch (linked-list and two-stacks versions) — Build — Queue
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Implement `LinkedQueue` (own nodes, `head` and `tail`) and
`TwoStackQueue` (two Python lists used only as stacks), both with
`enqueue(x)`, `dequeue()` (raise `IndexError` when empty), `peek()`,
`__len__`. Example: `enqueue(1); enqueue(2); dequeue()` → `1`. Then compare
with `collections.deque`.

**Must be able to explain:**
- [ ] Why `list.pop(0)` is a bad queue.
- [ ] Amortized cost of the two-stacks version.
- [ ] Why BFS needs a FIFO structure.

#### 7.2 Binary Tree Inorder Traversal — Easy — Trees / DFS  [LC 94](https://leetcode.com/problems/binary-tree-inorder-traversal/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the in-order traversal (left, node, right) of a binary
tree. Example: `root = [1,null,2,3]` → `[1,3,2]`. Solve recursively **and**
iteratively with an explicit stack.

**Must be able to explain:**
- [ ] What in-order gives you on a BST.
- [ ] How the explicit stack mirrors the recursion.

#### 7.3 Binary Tree Preorder Traversal — Easy — Trees / DFS  [LC 144](https://leetcode.com/problems/binary-tree-preorder-traversal/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the pre-order traversal (node, left, right). Example:
`[1,null,2,3]` → `[1,2,3]`. Recursive and iterative.

**Must be able to explain:**
- [ ] In which order children are pushed on the stack in the iterative version, and why.
- [ ] A use case (copying/serialising a tree).

#### 7.4 Binary Tree Postorder Traversal — Easy — Trees / DFS  [LC 145](https://leetcode.com/problems/binary-tree-postorder-traversal/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the post-order traversal (left, right, node). Example:
`[1,null,2,3]` → `[3,2,1]`. Recursive and iterative.

**Must be able to explain:**
- [ ] Why post-order is the natural order when a node needs its children's results.
- [ ] Why the iterative version is trickier than pre-order.

#### 7.5 Invert Binary Tree — Easy — Trees  [LC 226](https://leetcode.com/problems/invert-binary-tree/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Mirror a binary tree (swap left and right children everywhere)
and return the root. Example: `[4,2,7,1,3,6,9]` → `[4,7,2,9,6,3,1]`.

**Must be able to explain:**
- [ ] Recursive (DFS) and BFS versions.
- [ ] Time complexity and space in terms of tree height `h`.

#### 7.6 Maximum Depth of Binary Tree — Easy — Trees  [LC 104](https://leetcode.com/problems/maximum-depth-of-binary-tree/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the number of nodes on the longest root-to-leaf path.
Example: `[3,9,20,null,null,15,7]` → `3`.

**Must be able to explain:**
- [ ] Recursive DFS, iterative DFS and BFS versions.
- [ ] Worst-case recursion depth (skewed tree) and why that matters in Python.

#### 7.7 Diameter of Binary Tree — Easy — Trees  [LC 543](https://leetcode.com/problems/diameter-of-binary-tree/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the length (in edges) of the longest path between any
two nodes; it may not pass through the root. Example: `[1,2,3,4,5]` → `3`.

**Must be able to explain:**
- [ ] Why computing height separately at every node is O(n²).
- [ ] The difference between what the recursive function returns and what it records.

#### 7.8 Balanced Binary Tree — Easy — Trees  [LC 110](https://leetcode.com/problems/balanced-binary-tree/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return `True` if, for every node, the heights of the left and
right subtrees differ by at most 1. Example: `[3,9,20,null,null,15,7]` →
`True`; `[1,2,2,3,3,null,null,4,4]` → `False`.

**Must be able to explain:**
- [ ] The top-down O(n²) approach vs the bottom-up O(n) approach.
- [ ] How you return "height" and "is balanced" together.

#### 7.9 Same Tree — Easy — Trees  [LC 100](https://leetcode.com/problems/same-tree/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return `True` if two binary trees are structurally identical
with equal values. Example: `[1,2,3]` and `[1,2,3]` → `True`; `[1,2]` and
`[1,null,2]` → `False`.

**Must be able to explain:**
- [ ] All the base cases involving `None`.
- [ ] Time and space complexity.

#### 7.10 Subtree of Another Tree — Easy — Trees  [LC 572](https://leetcode.com/problems/subtree-of-another-tree/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return `True` if `subRoot` is identical to some subtree of
`root` (a node and all its descendants). Example: `root = [3,4,5,1,2]`,
`subRoot = [4,1,2]` → `True`.

**Must be able to explain:**
- [ ] How this reuses Same Tree and its O(m·n) complexity.
- [ ] (Stretch) How serialisation or hashing can make it faster.

#### 7.11 Lowest Common Ancestor of a Binary Search Tree — Medium — Trees / BST  [LC 235](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** In a BST, return the lowest node that has both `p` and `q` as
descendants (a node can be its own descendant). Example:
`root = [6,2,8,0,4,7,9,null,null,3,5], p = 2, q = 8` → `6`; `p = 2, q = 4` → `2`.

**Must be able to explain:**
- [ ] How the BST property tells you which way to go.
- [ ] Complexity in terms of height; iterative O(1)-space version.
- [ ] How the general binary tree version (LC 236) differs.

#### 7.12 Binary Tree Level Order Traversal — Medium — Trees / BFS  [LC 102](https://leetcode.com/problems/binary-tree-level-order-traversal/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return node values level by level, left to right. Example:
`[3,9,20,null,null,15,7]` → `[[3],[9,20],[15,7]]`.

**Must be able to explain:**
- [ ] How you know where one level ends in the queue.
- [ ] Maximum queue size (widest level) and the space complexity.

#### 7.13 Binary Tree Right Side View — Medium — Trees / BFS  [LC 199](https://leetcode.com/problems/binary-tree-right-side-view/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the values visible when looking at the tree from the
right side, top to bottom. Example: `[1,2,3,null,5,null,4]` → `[1,3,4]`.

**Must be able to explain:**
- [ ] Why "just follow right children" is wrong (give a counter-example).
- [ ] Both a BFS and a DFS way to solve it.

#### 7.14 Count Good Nodes in Binary Tree — Medium — Trees / DFS  [LC 1448](https://leetcode.com/problems/count-good-nodes-in-binary-tree/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** A node is "good" if no node on the path from the root to it has
a greater value. Return the number of good nodes. Example:
`[3,1,4,3,null,1,5]` → `4`.

**Must be able to explain:**
- [ ] What state you pass **down** the recursion (vs returning up).
- [ ] Time and space complexity.

#### 7.15 Validate Binary Search Tree — Medium — Trees / BST  [LC 98](https://leetcode.com/problems/validate-binary-search-tree/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return `True` if the tree is a valid BST (left subtree values
strictly less, right subtree values strictly greater, recursively).
Example: `[2,1,3]` → `True`; `[5,1,4,null,null,3,6]` → `False`.

**Must be able to explain:**
- [ ] Why checking only a node against its direct children is wrong (counter-example).
- [ ] The "valid range" idea and the in-order idea — both approaches.

#### 7.16 Kth Smallest Element in a BST — Medium — Trees / BST  [LC 230](https://leetcode.com/problems/kth-smallest-element-in-a-bst/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Return the `k`-th smallest value (1-indexed) in a BST. Example:
`root = [3,1,4,null,2], k = 1` → `1`.

**Must be able to explain:**
- [ ] Why in-order traversal is the key, and how to stop early.
- [ ] Complexity O(h + k).
- [ ] Follow-up: what you would store in nodes if the BST is modified often and queried often.

#### 7.17 Construct Binary Tree from Preorder and Inorder Traversal — Medium — Trees  [LC 105](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Given pre-order and in-order traversals of a tree with unique
values, rebuild the tree. Example: `preorder = [3,9,20,15,7]`,
`inorder = [9,3,15,20,7]` → `[3,9,20,null,null,15,7]`.

**Must be able to explain:**
- [ ] What pre-order tells you and what in-order tells you.
- [ ] Why slicing lists makes it O(n²) and how an index map fixes it.

#### 7.18 Binary Tree Maximum Path Sum — Hard — Trees / DFS — **OPTIONAL**  [LC 124](https://leetcode.com/problems/binary-tree-maximum-path-sum/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** A path is any sequence of connected nodes (each at most once),
not necessarily through the root. Return the maximum path sum. Example:
`[-10,9,20,null,null,15,7]` → `42` (`15 → 20 → 7`).

**Must be able to explain:**
- [ ] The difference between the path you can **return** to the parent and the path you can **record** as a candidate.
- [ ] How negative subtrees are handled.

#### 7.19 Serialize and Deserialize Binary Tree — Hard — Trees — **OPTIONAL**  [LC 297](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/)
- [ ] Solved · [ ] R1 · [ ] R3 · [ ] R7

**Problem:** Design `serialize(root) -> str` and `deserialize(str) -> root`
so that any binary tree round-trips exactly. Example: `[1,2,3,null,null,4,5]`
→ string → the same tree.

**Must be able to explain:**
- [ ] Why you must record `None` children.
- [ ] Pre-order vs level-order formats.
- [ ] Complexity of both directions.

### Module checklist — I can…
- [ ] Write pre-, in- and post-order traversals recursively and iteratively from a blank file.
- [ ] Write level-order BFS with a queue and process one level at a time.
- [ ] Decide whether information should flow down (parameters) or up (return values).
- [ ] Explain and use the BST property for search, validation and k-th smallest.
- [ ] State time O(n) and space O(h) for typical tree recursions, and when h = n.

**Estimated hours:** ~25h

### Self-check interview questions
1. What is the difference between depth and height of a node?
2. Name the three DFS traversals and one use case for each.
3. When would you use BFS instead of DFS on a tree?
4. What is a BST, and what are the complexities of search/insert/delete — balanced vs skewed?
5. What does "balanced" mean, and name two self-balancing trees.
6. Why is the space complexity of recursive tree DFS O(h)?
7. How do you delete a node with two children from a BST?
8. Can you rebuild a binary tree from pre-order and post-order alone? Why or why not?

---

**Answers**
1. Depth = number of edges from the root down to the node. Height = number of edges on the longest path from the node down to a leaf.
2. Pre-order (node, left, right): copying/serialising a tree. In-order (left, node, right): sorted output from a BST. Post-order (left, right, node): computing values that depend on children (sizes, heights, deleting a tree).
3. When you need level-by-level information or the shortest path in number of edges (e.g. minimum depth), or when the tree is very deep and recursion would overflow.
4. A binary tree where every node's left subtree has smaller values and right subtree larger values. O(log n) when balanced, O(n) when skewed (e.g. inserting sorted data).
5. For every node the subtree heights differ by a bounded amount, keeping height O(log n). AVL trees and red-black trees.
6. The call stack holds one frame per node on the current root-to-node path, and that path is at most the height h.
7. Replace its value with its in-order successor (smallest node in the right subtree) or predecessor, then delete that successor node, which has at most one child.
8. Not in general: without in-order you cannot tell whether a single child is a left or a right child. It works only for full binary trees (every node has 0 or 2 children).

## Module 8 — Tries (~6h)

**Topics:** trie node structure (children map + end-of-word flag), insert / search / prefix search, wildcard search, trie vs hash set trade-offs, memory cost of tries.

### Theory
- [ ] **L8.1 Trie structure** — NeetCode *Advanced Algorithms* → "Trie" lesson. Draw the trie for `["cat", "car", "cart", "dog"]` by hand before coding anything.
- [ ] **L8.2 Trie vs hash set** — compare "is `w` a word?" and "does any word start with `p`?" for both structures, including time and memory. NeetCode video: "Implement Trie (Prefix Tree)" (neetcode.io/roadmap → Tries).

### Problems

#### 8.1 Longest Common Prefix — Easy — Strings / Trie warm-up  [LC 14](https://leetcode.com/problems/longest-common-prefix/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given a list of strings, return the longest prefix that all of them share. If there is none, return `""`.
Input: `["flower", "flow", "flight"]` → Output: `"fl"`
**Must be able to explain:**
- [ ] At least two different approaches and their time complexity in terms of total characters
- [ ] How the answer relates to the shortest string in the list
- [ ] Edge cases: empty list, one string, an empty string in the list

#### 8.2 Implement Trie (Prefix Tree) — Medium — Tries  [LC 208](https://leetcode.com/problems/implement-trie-prefix-tree/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Implement a class `Trie` with `insert(word)`, `search(word)` (true only for an inserted whole word) and `startsWith(prefix)` (true if any inserted word starts with the prefix).
Input: `insert("apple")`, `search("apple")`, `search("app")`, `startsWith("app")`, `insert("app")`, `search("app")` → Output: `true, false, true, true`
**Must be able to explain:**
- [ ] Why `search("app")` and `startsWith("app")` give different answers here
- [ ] Time complexity of each operation in terms of word length `L`
- [ ] Choosing a `dict` or a fixed array of 26 for children, and the trade-off

#### 8.3 Design Add and Search Words Data Structure — Medium — Tries  [LC 211](https://leetcode.com/problems/design-add-and-search-words-data-structure/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Implement `WordDictionary` with `addWord(word)` and `search(word)`. The search pattern may contain `.`, which matches any single letter.
Input: `addWord("bad")`, `addWord("dad")`, `addWord("mad")`, `search("pad")`, `search("bad")`, `search(".ad")`, `search("b..")` → Output: `false, true, true, true`
**Must be able to explain:**
- [ ] What changes in the search once `.` is allowed
- [ ] Worst-case time complexity of a search made only of dots
- [ ] Why a plain hash set of words is a poor fit for this problem

#### 8.4 Word Search II — Hard — Backtracking + Trie  [LC 212](https://leetcode.com/problems/word-search-ii/)  **OPTIONAL** (do it after Module 10)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given an `m x n` board of letters and a list of words, return every word that can be built from sequentially adjacent cells (horizontal or vertical). A cell may be used at most once per word.
Input: `board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]]`, `words = ["oath","pea","eat","rain"]` → Output: `["eat","oath"]`
**Must be able to explain:**
- [ ] Why running Word Search (10.7) once per word is too slow, with the complexity
- [ ] How the trie is combined with the board search
- [ ] Pruning ideas that keep the search from repeating work, and how you avoid duplicate answers

### Module 8 checklist — must be able to do/explain
- [ ] Implement a trie from a blank file in under 15 minutes
- [ ] Explain when a trie beats a hash set, and when it does not
- [ ] State the time and space complexity of trie operations

**Estimated hours:** ~6h

### Self-check interview questions
1. What is a trie, and what does each node store?
2. What is the complexity of insert and search in a trie holding `N` words of average length `L`?
3. When would you choose a trie over a `set` of strings?
4. Why is a trie memory-hungry, and how can you reduce that?
5. Give two real-world uses of tries.
6. How would you support deleting a word from a trie?

---
**Answers**
1. A tree where each edge is a character. A node stores its children (char → node) and a flag marking whether a word ends there. The root is the empty prefix.
2. O(L) per operation, whatever `N` is. Space is O(total characters) in the worst case.
3. When you need prefix queries (autocomplete, "any word starting with…"), lexicographic walks, or a wildcard or character-by-character search that shares work between words. For exact membership only, a `set` is simpler and usually faster.
4. Every node carries its own container of children, which costs a lot of overhead per character. Ways to reduce it: compressed (radix) tries, arrays for small alphabets, or `__slots__` in Python.
5. Autocomplete and search suggestions, spell checkers, IP routing (longest-prefix match), word games, T9 input.
6. Walk down to the last node and clear its end-of-word flag. Then, on the way back up, remove any node that has no children and is not the end of another word.

---

## Module 9 — Heap / Priority Queue (~12h)

**Topics:** heap properties (complete binary tree plus heap order), array representation and index formulas, sift-up / sift-down, O(n) heapify, Python `heapq` (min-heap only, tuples, negation for max-heap), top-k patterns, the two-heaps pattern, heaps inside design problems.

### Theory
- [ ] **L9.1 Heap properties** — NeetCode *Algorithms & Data Structures for Beginners* → "Heap Properties". Write down the parent/left/right index formulas for a 0-indexed array.
- [ ] **L9.2 Push and pop** — NeetCode *Beginners* → "Push and Pop". Trace sift-up and sift-down by hand on `[1, 3, 5, 7, 9]`.
- [ ] **L9.3 Heapify** — NeetCode *Beginners* → "Heapify". Be able to argue why building a heap is O(n) and not O(n log n).
- [ ] **L9.4 Python `heapq`** — [docs.python.org/3/library/heapq.html](https://docs.python.org/3/library/heapq.html): `heappush`, `heappop`, `heapify`, `heappushpop`, `nlargest`/`nsmallest`, tuple priorities, max-heap by negation.
- [ ] **L9.5 Two heaps** — NeetCode *Advanced Algorithms* → "Two Heaps".

### Problems

#### 9.1 Implement a binary MinHeap from scratch — Easy — Heap implementation
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Write a class `MinHeap` backed by a Python list, **without** `heapq`. It needs `push(x)`, `pop()` (remove and return the smallest), `peek()`, `__len__`, and a classmethod `heapify(items)` that builds a heap in O(n). In `tests()`, compare it with `heapq` on 1,000 random lists.
Input: `push(5)`, `push(3)`, `push(8)`, `push(1)`, `pop()`, `pop()` → Output: `1, 3`
**Must be able to explain:**
- [ ] The parent and child index formulas, and why a complete tree fits in an array with no gaps
- [ ] Why `push` and `pop` are O(log n) and `peek` is O(1)
- [ ] Why `heapify` is O(n)
- [ ] What happens when you `pop` from an empty heap, and what your class does in that case

#### 9.2 Take Gifts From the Richest Pile — Easy — Heap  [LC 2558](https://leetcode.com/problems/take-gifts-from-the-richest-pile/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** `gifts[i]` is the size of pile `i`. Every second, pick the pile with the most gifts and leave `floor(sqrt(size))` gifts in it. After `k` seconds, return the total number of gifts left.
Input: `gifts = [25, 64, 9, 4, 100]`, `k = 4` → Output: `29`
**Must be able to explain:**
- [ ] How you get max-heap behaviour out of Python's min-heap
- [ ] Time complexity in terms of `n` and `k`
- [ ] Why re-sorting after every step is worse

#### 9.3 Kth Largest Element in a Stream — Easy — Heap  [LC 703](https://leetcode.com/problems/kth-largest-element-in-a-stream/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Design `KthLargest(k, nums)` with `add(val)`, which inserts `val` into the stream and returns the current k-th largest element.
Input: `k = 3`, `nums = [4, 5, 8, 2]`; `add(3)`, `add(5)`, `add(10)`, `add(9)`, `add(4)` → Output: `4, 5, 5, 8, 8`
**Must be able to explain:**
- [ ] Which heap type and size you keep, and why
- [ ] Time complexity per `add` and space complexity
- [ ] How this generalises to "top-k over an unbounded stream"

#### 9.4 Last Stone Weight — Easy — Heap  [LC 1046](https://leetcode.com/problems/last-stone-weight/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** On each turn, smash the two heaviest stones together. If their weights are equal, both are destroyed. Otherwise the lighter one is destroyed and the heavier one's weight becomes the difference. Return the weight of the last stone left, or 0 if none are left.
Input: `stones = [2, 7, 4, 1, 8, 1]` → Output: `1`
**Must be able to explain:**
- [ ] Why a heap and not sorting on every turn
- [ ] Overall time complexity
- [ ] What the simulation loop does when exactly one stone is left, and when none are

#### 9.5 K Closest Points to Origin — Medium — Heap  [LC 973](https://leetcode.com/problems/k-closest-points-to-origin/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given points `[x, y]` and an integer `k`, return the `k` points closest to `(0, 0)` by Euclidean distance. The answer may be in any order.
Input: `points = [[1, 3], [-2, 2]]`, `k = 1` → Output: `[[-2, 2]]`
**Must be able to explain:**
- [ ] Why you don't need `sqrt` to compare distances
- [ ] O(n log n) vs O(n log k) approaches, and which heap type each uses
- [ ] How Python compares tuples when two distances are equal

#### 9.6 Kth Largest Element in an Array — Medium — Heap / Quickselect  [LC 215](https://leetcode.com/problems/kth-largest-element-in-an-array/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the k-th largest element of an unsorted array (by sorted position, so duplicates count).
Input: `nums = [3, 2, 1, 5, 6, 4]`, `k = 2` → Output: `5`
**Must be able to explain:**
- [ ] The sorting, heap and quickselect approaches and their complexities (average and worst case)
- [ ] Why quickselect's worst case is O(n²) and how a random pivot helps
- [ ] Which approach you'd pick in an interview, and why

#### 9.7 Task Scheduler — Medium — Heap / Greedy  [LC 621](https://leetcode.com/problems/task-scheduler/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given CPU tasks labelled with letters and a cooldown `n`, the same task must be at least `n` intervals apart. Each interval runs one task or idles. Return the minimum number of intervals needed to finish all tasks.
Input: `tasks = ["A","A","A","B","B","B"]`, `n = 2` → Output: `8` (A B idle A B idle A B)
**Must be able to explain:**
- [ ] Why the most frequent task drives the answer
- [ ] How time and cooldowns are tracked in your approach
- [ ] Time complexity, given the alphabet has only 26 letters

#### 9.8 Design Twitter — Medium — Design / Heap  [LC 355](https://leetcode.com/problems/design-twitter/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Design a simplified Twitter with `postTweet(userId, tweetId)`, `getNewsFeed(userId)` (the 10 most recent tweet ids from the user and the people they follow, newest first), `follow(followerId, followeeId)` and `unfollow(followerId, followeeId)`.
Input: `postTweet(1,5)`, `getNewsFeed(1)`, `follow(1,2)`, `postTweet(2,6)`, `getNewsFeed(1)`, `unfollow(1,2)`, `getNewsFeed(1)` → Output: `[5]`, `[6,5]`, `[5]`
**Must be able to explain:**
- [ ] The data structures you chose for follows and for tweets, and why
- [ ] How "most recent" is decided without real timestamps
- [ ] Complexity of `getNewsFeed` in terms of followees `F`
- [ ] How this links to fan-out-on-write vs fan-out-on-read in real system design

#### 9.9 Find Median from Data Stream — Hard — Two Heaps  [LC 295](https://leetcode.com/problems/find-median-from-data-stream/)  **OPTIONAL**
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Design `MedianFinder` with `addNum(num)` and `findMedian()`, which returns the median of every number added so far. With an even count, the median is the mean of the two middle values.
Input: `addNum(1)`, `addNum(2)`, `findMedian()`, `addNum(3)`, `findMedian()` → Output: `1.5, 2.0`
**Must be able to explain:**
- [ ] The invariant(s) your structure keeps after every insert
- [ ] Time complexity of `addNum` and `findMedian`
- [ ] Why keeping a sorted list and using `bisect.insort` is O(n) per insert

### Module 9 checklist — must be able to do/explain
- [ ] Implement a min-heap from a blank file, including sift-up, sift-down and heapify
- [ ] Explain heap vs sorted array vs balanced BST for priority-queue operations
- [ ] Recognise "top-k", "k-th", "merge k sorted" and "running median" as heap problems
- [ ] Use `heapq` correctly with tuples and negation

**Estimated hours:** ~12h

### Self-check interview questions
1. What two properties define a binary heap?
2. For a 0-indexed array heap, what are the parent and child indices of node `i`?
3. Why is building a heap O(n)?
4. How do you get a max-heap in Python?
5. Is a heap sorted? What can you get in O(1)?
6. Heap vs BST for a priority queue: what are the trade-offs?
7. How would you find the top 10 most frequent words in a 100 GB log file?
8. Where do heaps appear in real systems?

---
**Answers**
1. Shape: it is a complete binary tree, with every level full except possibly the last, which fills left to right. Order: every parent is ≤ its children (in a min-heap).
2. Parent is `(i - 1) // 2`, left child `2i + 1`, right child `2i + 2`.
3. Heapify sifts down from the last parent up to the root. Most nodes are near the bottom and only move a short distance. The sum of the heights, about n/2·1 + n/4·2 + …, is bounded by O(n).
4. Push negated values (`-x`) and negate them again on pop, or push tuples with a negated key. `heapq` only provides a min-heap.
5. No. It is only partially ordered. You get the min (or max) in O(1) with `heap[0]`. Everything else needs pops.
6. A heap gives O(1) peek, O(log n) push/pop, fits in a compact array and has good cache behaviour, but searching or deleting an arbitrary element is O(n). A balanced BST gives O(log n) for min, max, search, arbitrary delete and ordered iteration, at the cost of more memory and complexity.
7. Count words in chunks (hash maps, possibly sharded by hash of the word across files or machines), then keep a size-10 min-heap over the counts. This is a streaming / map-reduce style top-k.
8. OS schedulers, timers and delayed-job queues (Celery ETA and similar), Dijkstra/A*, merging sorted files in external sort, rate limiters and bandwidth schedulers.

---

## Module 10 — Backtracking (~15h)

**Topics:** decision trees, choose → explore → un-choose, subsets / combinations / permutations, duplicate inputs, pruning, grid backtracking, time complexity of exponential searches (2ⁿ, n!), recursion depth in Python.

### Theory
- [ ] **L10.1 Backtracking as a decision tree** — NeetCode *Beginners* → "Tree Maze". Draw the full decision tree for the subsets of `[1, 2, 3]`.
- [ ] **L10.2 Subsets** — NeetCode *Advanced Algorithms* → "Subsets".
- [ ] **L10.3 Combinations** — NeetCode *Advanced Algorithms* → "Combinations".
- [ ] **L10.4 Permutations** — NeetCode *Advanced Algorithms* → "Permutations".
- [ ] **L10.5 Recursion refresher** — *Grokking Algorithms* (2nd ed.) Ch. 3 "Recursion": base case, recursive case, the call stack. Why copying the current path matters when you record a result.
- [ ] **L10.6 Complexity and pruning** — count the leaves of each decision tree you drew, and explain why output size puts a lower bound on the runtime.

### Problems

#### 10.1 Generate all binary strings of length n — Easy — Backtracking warm-up
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Without `itertools`, return every string of `0`s and `1`s of length `n`, in any order.
Input: `n = 2` → Output: `["00", "01", "10", "11"]`
**Must be able to explain:**
- [ ] Draw the recursion tree for `n = 3`
- [ ] Time complexity including the cost of building the strings
- [ ] How many frames the call stack holds at most

#### 10.2 Subsets — Medium — Backtracking  [LC 78](https://leetcode.com/problems/subsets/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given distinct integers, return every possible subset (the power set). The answer must not contain duplicate subsets.
Input: `[1, 2, 3]` → Output: `[[], [1], [2], [1,2], [3], [1,3], [2,3], [1,2,3]]` (any order)
**Must be able to explain:**
- [ ] The decision made at each level of your tree
- [ ] Why the answer has 2ⁿ subsets, and the total time complexity
- [ ] The bug you get if you append the path list itself instead of a copy

#### 10.3 Combination Sum — Medium — Backtracking  [LC 39](https://leetcode.com/problems/combination-sum/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given distinct positive `candidates` and a `target`, return every unique combination that sums to `target`. The same number may be used any number of times.
Input: `candidates = [2, 3, 6, 7]`, `target = 7` → Output: `[[2, 2, 3], [7]]`
**Must be able to explain:**
- [ ] How you avoid producing `[2,2,3]` and `[3,2,2]` as separate answers
- [ ] Where you prune, and why the numbers being positive makes that possible
- [ ] A reasonable bound on the depth of the recursion

#### 10.4 Combination Sum II — Medium — Backtracking  [LC 40](https://leetcode.com/problems/combination-sum-ii/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Like 10.3, but `candidates` may contain duplicates and each element may be used **at most once**. The answer must not contain duplicate combinations.
Input: `candidates = [10, 1, 2, 7, 6, 1, 5]`, `target = 8` → Output: `[[1,1,6], [1,2,5], [1,7], [2,6]]`
**Must be able to explain:**
- [ ] Exactly what changes from 10.3 and why
- [ ] How duplicate combinations get avoided without a `set` of results
- [ ] Why deduplicating at the end with a `set` is a weaker solution

#### 10.5 Permutations — Medium — Backtracking  [LC 46](https://leetcode.com/problems/permutations/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given distinct integers, return every permutation in any order.
Input: `[1, 2, 3]` → Output: `[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]`
**Must be able to explain:**
- [ ] How the decision tree differs from the subsets tree
- [ ] Why the time complexity is O(n · n!)
- [ ] How you track which elements are already used

#### 10.6 Subsets II — Medium — Backtracking  [LC 90](https://leetcode.com/problems/subsets-ii/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given integers that may contain duplicates, return every possible subset with no duplicate subsets.
Input: `[1, 2, 2]` → Output: `[[], [1], [1,2], [1,2,2], [2], [2,2]]`
**Must be able to explain:**
- [ ] Why the duplicate subsets appear in the first place, by drawing the tree
- [ ] What preprocessing you do and why it is needed
- [ ] The connection to Combination Sum II

#### 10.7 Word Search — Medium — Backtracking  [LC 79](https://leetcode.com/problems/word-search/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given an `m x n` board of letters and a word, return true if the word can be built from sequentially adjacent cells (up, down, left, right), using each cell at most once.
Input: `board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]`, `word = "ABCCED"` → Output: `true`
**Must be able to explain:**
- [ ] How you mark a cell as used during one path and release it afterwards
- [ ] Time complexity in terms of `m·n` and word length `L`
- [ ] Early exits worth adding (for example, a letter-count check before searching)

#### 10.8 Palindrome Partitioning — Medium — Backtracking  [LC 131](https://leetcode.com/problems/palindrome-partitioning/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Split string `s` so that every piece is a palindrome, and return every such split.
Input: `s = "aab"` → Output: `[["a","a","b"], ["aa","b"]]`
**Must be able to explain:**
- [ ] What one "choice" means at each step of the recursion
- [ ] The worst-case number of partitions (think `"aaaa…"`)
- [ ] How the repeated palindrome checks could be cached or precomputed

#### 10.9 Letter Combinations of a Phone Number — Medium — Backtracking  [LC 17](https://leetcode.com/problems/letter-combinations-of-a-phone-number/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given a string of digits `2–9`, return every letter combination they could spell on a phone keypad. For empty input, return `[]`.
Input: `"23"` → Output: `["ad","ae","af","bd","be","bf","cd","ce","cf"]`
**Must be able to explain:**
- [ ] Time complexity, given that digits map to 3 or 4 letters
- [ ] The empty-input edge case
- [ ] An iterative (non-recursive) alternative and how it compares

#### 10.10 N-Queens — Hard — Backtracking  [LC 51](https://leetcode.com/problems/n-queens/)  **OPTIONAL**
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Place `n` queens on an `n x n` chessboard so that no two attack each other. Return every distinct board, using `"Q"` and `"."`.
Input: `n = 4` → Output: `[[".Q..","...Q","Q...","..Q."], ["..Q.","Q...","...Q",".Q.."]]`
**Must be able to explain:**
- [ ] How you check "is this square attacked?" in O(1)
- [ ] Why you only ever try one queen per row
- [ ] Rough complexity, and why it is far less than trying every placement

### Module 10 checklist — must be able to do/explain
- [ ] Write a backtracking template (choose / explore / un-choose) from memory
- [ ] Tell subsets, combinations and permutations apart, and draw each tree
- [ ] Handle duplicates in the input without deduplicating the output afterwards
- [ ] Estimate exponential complexity from the tree's branching factor and depth

**Estimated hours:** ~15h

### Self-check interview questions
1. What is backtracking, and how is it different from plain recursion or brute force?
2. What are the three steps in every backtracking function?
3. How many subsets and how many permutations does a set of `n` elements have?
4. Why do you append a copy of the current path to the results?
5. How do you avoid duplicate results when the input has duplicates?
6. What is pruning? Give an example.
7. What are the risks of deep recursion in Python, and how do you mitigate them?

---
**Answers**
1. Backtracking builds candidate solutions step by step and abandons (backs out of) a partial candidate as soon as it cannot lead to a valid answer. Brute force produces every complete candidate first and filters afterwards.
2. Choose (add an option to the path), explore (recurse), un-choose (undo the change before trying the next option).
3. 2ⁿ subsets and n! permutations.
4. The path list gets mutated as the search continues. Storing the reference means every stored result ends up showing the final (usually empty) state.
5. Sort the input, then at the same recursion level skip any element equal to the previous one. That way each distinct value is tried only once per position.
6. Cutting off a branch early when it provably cannot succeed. Examples: stop when the running sum exceeds the target (with positive numbers), or stop when the partial palindrome check fails.
7. Recursion is limited to about 1,000 frames by default, each frame has overhead, and you get a `RecursionError`. Mitigations: an explicit stack (iterative version), `sys.setrecursionlimit` with care, or restating the problem so the recursion is shallower.

---

## Module 11 — Graphs (~22h)

**Topics:** graph vocabulary, adjacency list / matrix / grid, DFS (recursive and iterative), BFS with `deque`, shortest path in an unweighted graph, multi-source BFS, connected components, cycle detection, topological sort, Union-Find (path compression, union by rank/size).

### Theory — do these BEFORE the problems
- [ ] **L11.1 Graph basics and representations** — NeetCode *Beginners* → "Intro to Graphs" and "Adjacency List". Build an adjacency list from an edge list by hand.
- [ ] **L11.2 DFS** — NeetCode *Beginners* → "Matrix DFS"; NeetCode *Advanced* → "Iterative DFS". Write both recursive and iterative DFS on a small grid.
- [ ] **L11.3 BFS** — NeetCode *Beginners* → "Matrix BFS"; *Grokking Algorithms* (2nd ed.) Ch. 6 "Breadth-first search". Why BFS gives shortest paths in unweighted graphs; `collections.deque` vs `list.pop(0)`.
- [ ] **L11.4 Multi-source BFS** — the idea of starting BFS from many cells at once (NeetCode video "Rotting Oranges").
- [ ] **L11.5 Topological sort and cycle detection** — NeetCode *Advanced* → "Topological Sort". Both Kahn's (in-degree) and DFS three-colour versions, in theory.
- [ ] **L11.6 Union-Find** — NeetCode *Advanced* → "Union-Find". Implement `find` with path compression and `union` by rank/size as a standalone class.

### Problems

#### 11.1 Flood Fill — Easy — Graphs DFS/BFS  [LC 733](https://leetcode.com/problems/flood-fill/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given an image grid, a start pixel `(sr, sc)` and a `color`, repaint the start pixel and every pixel connected to it 4-directionally that has the same original colour.
Input: `image = [[1,1,1],[1,1,0],[1,0,1]]`, `sr = 1`, `sc = 1`, `color = 2` → Output: `[[2,2,2],[2,2,0],[2,0,1]]`
**Must be able to explain:**
- [ ] The infinite-loop trap when the new colour equals the old one
- [ ] DFS vs BFS here, and whether the choice matters
- [ ] Time and space complexity

#### 11.2 Find if Path Exists in Graph — Easy — Graphs  [LC 1971](https://leetcode.com/problems/find-if-path-exists-in-graph/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given `n` vertices, a list of undirected `edges`, a `source` and a `destination`, return whether a path connects them.
Input: `n = 3`, `edges = [[0,1],[1,2],[2,0]]`, `source = 0`, `destination = 2` → Output: `true`
**Must be able to explain:**
- [ ] How you build the adjacency list, and its size
- [ ] Why the visited set is required
- [ ] Solve it three ways: DFS, BFS and Union-Find, with the complexity of each

#### 11.3 Number of Islands — Medium — Graphs DFS/BFS  [LC 200](https://leetcode.com/problems/number-of-islands/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given a grid of `"1"` (land) and `"0"` (water), count the islands. An island is a group of land cells connected horizontally or vertically.
Input: `[["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]` → Output: `3`
**Must be able to explain:**
- [ ] Why each cell is processed only once, and the resulting O(m·n)
- [ ] Whether mutating the input grid is acceptable, and what the alternative is
- [ ] Worst-case recursion depth, and when you would switch to BFS

#### 11.4 Max Area of Island — Medium — Graphs  [LC 695](https://leetcode.com/problems/max-area-of-island/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given a 0/1 grid, return the area (cell count) of the largest island, or 0 if there is no land.
Input: `[[0,1,1,0],[0,1,0,0],[0,0,0,1]]` → Output: `3`
**Must be able to explain:**
- [ ] How the traversal returns or accumulates the area
- [ ] What is different from 11.3
- [ ] Complexity

#### 11.5 Clone Graph — Medium — Graphs  [LC 133](https://leetcode.com/problems/clone-graph/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given a reference to one node of a connected undirected graph (each node has `val` and a `neighbors` list), return a deep copy of the whole graph.
Input: adjacency list `[[2,4],[1,3],[2,4],[1,3]]` → Output: a new graph with the same structure (`[[2,4],[1,3],[2,4],[1,3]]`) made of new node objects
**Must be able to explain:**
- [ ] How you avoid cloning a node twice and avoid looping forever on cycles
- [ ] Why the old→new mapping is the key data structure
- [ ] How to test that the result really is a deep copy

#### 11.6 Islands and Treasure (Walls and Gates) — Medium — Graphs BFS  [NeetCode](https://neetcode.io/problems/islands-and-treasure) (LC 286, premium)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** In a grid, `-1` is a wall, `0` is a treasure/gate and `INF = 2147483647` is an empty room. Fill each empty room in place with its distance to the nearest gate. Rooms that can't reach a gate stay `INF`.
Input: `[[INF,-1,0,INF],[INF,INF,INF,-1],[INF,-1,INF,-1],[0,-1,INF,INF]]` → Output: `[[3,-1,0,1],[2,2,1,-1],[1,-1,2,-1],[0,-1,3,4]]`
**Must be able to explain:**
- [ ] Why starting a separate search from each empty room is slow, with the complexity
- [ ] Why BFS gives correct shortest distances here and DFS does not
- [ ] Final time complexity

#### 11.7 Rotting Oranges — Medium — Graphs BFS  [LC 994](https://leetcode.com/problems/rotting-oranges/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Cells are `0` (empty), `1` (fresh) or `2` (rotten). Each minute, every fresh orange next to a rotten one becomes rotten. Return the minutes until no fresh orange is left, or `-1` if that is impossible.
Input: `[[2,1,1],[1,1,0],[0,1,1]]` → Output: `4`
**Must be able to explain:**
- [ ] How you count minutes with BFS levels
- [ ] How you detect the `-1` case
- [ ] The edge case of zero fresh oranges at the start

#### 11.8 Pacific Atlantic Water Flow — Medium — Graphs  [LC 417](https://leetcode.com/problems/pacific-atlantic-water-flow/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given an `m x n` height map, the Pacific touches the top and left edges and the Atlantic touches the bottom and right edges. Water flows to an adjacent cell of equal or lower height. Return the cells from which water can reach both oceans.
Input: `[[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],[5,1,1,2,4]]` → Output: `[[0,4],[1,3],[1,4],[2,2],[3,0],[3,1],[4,0]]`
**Must be able to explain:**
- [ ] Why searching from every cell is O((m·n)²)
- [ ] The reversed direction of thinking and why it is valid
- [ ] How the two results are combined

#### 11.9 Surrounded Regions — Medium — Graphs  [LC 130](https://leetcode.com/problems/surrounded-regions/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given a board of `"X"` and `"O"`, capture every region of `"O"` that is fully surrounded by `"X"` by flipping it to `"X"`. Regions touching the border are not captured.
Input: `[["X","X","X","X"],["X","O","O","X"],["X","X","O","X"],["X","O","X","X"]]` → Output: `[["X","X","X","X"],["X","X","X","X"],["X","X","X","X"],["X","O","X","X"]]`
**Must be able to explain:**
- [ ] Which cells are "safe", and how you find them
- [ ] How many passes over the board you make, and the complexity
- [ ] The link to 11.8

#### 11.10 Course Schedule — Medium — Topological Sort  [LC 207](https://leetcode.com/problems/course-schedule/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** There are `numCourses` courses. `prerequisites[i] = [a, b]` means you must take `b` before `a`. Return whether you can finish every course.
Input: `numCourses = 2`, `prerequisites = [[1,0],[0,1]]` → Output: `false` (with `[[1,0]]` the answer is `true`)
**Must be able to explain:**
- [ ] Why the question is really "does the directed graph have a cycle?"
- [ ] Both approaches from L11.5, and how each one detects a cycle
- [ ] Time complexity O(V + E)

#### 11.11 Course Schedule II — Medium — Topological Sort  [LC 210](https://leetcode.com/problems/course-schedule-ii/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Same setup as 11.10, but return one valid order for taking every course, or `[]` if that is impossible.
Input: `numCourses = 4`, `prerequisites = [[1,0],[2,0],[3,1],[3,2]]` → Output: `[0,1,2,3]` (or `[0,2,1,3]`)
**Must be able to explain:**
- [ ] Why more than one valid answer can exist
- [ ] How the order is produced, and in which direction your edges point
- [ ] A real-world use: build systems, migrations, Celery chains, dependency resolution in `pip`

#### 11.12 Graph Valid Tree — Medium — Union-Find / Graphs  [NeetCode](https://neetcode.io/problems/valid-tree) (LC 261, premium)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given `n` nodes labelled `0..n-1` and a list of undirected edges, return whether the edges form a valid tree.
Input: `n = 5`, `edges = [[0,1],[0,2],[0,3],[1,4]]` → Output: `true`; `n = 5`, `edges = [[0,1],[1,2],[2,3],[1,3],[1,4]]` → Output: `false`
**Must be able to explain:**
- [ ] The two conditions that make an undirected graph a tree
- [ ] A quick check on the number of edges, and why it alone isn't enough
- [ ] How cycles are detected in an undirected graph (why "parent" matters in DFS)

#### 11.13 Number of Connected Components in an Undirected Graph — Medium — Union-Find  [NeetCode](https://neetcode.io/problems/count-connected-components) (LC 323, premium)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given `n` nodes and a list of undirected edges, return the number of connected components.
Input: `n = 5`, `edges = [[0,1],[1,2],[3,4]]` → Output: `2`
**Must be able to explain:**
- [ ] Solve it with DFS and with Union-Find, and compare
- [ ] The complexity of Union-Find with path compression + union by rank (inverse Ackermann)
- [ ] When Union-Find is the better choice (edges arriving online, as a stream)

#### 11.14 Redundant Connection — Medium — Union-Find  [LC 684](https://leetcode.com/problems/redundant-connection/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** A tree with `n` nodes had one extra edge added, which creates exactly one cycle. Return the edge that can be removed to leave a tree. If several qualify, return the one that appears last in the input.
Input: `edges = [[1,2],[1,3],[2,3]]` → Output: `[2,3]`
**Must be able to explain:**
- [ ] Why processing edges in order naturally finds the "last" answer
- [ ] What `union` returning false means
- [ ] The complexity compared with a DFS-per-edge approach

#### 11.15 Word Ladder — Hard — Graphs BFS  [LC 127](https://leetcode.com/problems/word-ladder/)  **OPTIONAL**
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given `beginWord`, `endWord` and a `wordList`, return the number of words in the shortest transformation sequence from begin to end. Each step changes exactly one letter, and every intermediate word must be in the list. Return 0 if there is no such sequence.
Input: `beginWord = "hit"`, `endWord = "cog"`, `wordList = ["hot","dot","dog","lot","log","cog"]` → Output: `5` (hit → hot → dot → dog → cog)
**Must be able to explain:**
- [ ] What the vertices and edges of the implicit graph are
- [ ] Why building all pairwise edges naively is O(N²·L), and a faster way to find neighbours
- [ ] Why BFS, and what bidirectional BFS would improve

### Module 11 checklist — must be able to do/explain
- [ ] Convert an edge list or grid into something you can traverse, from a blank file
- [ ] Write DFS (recursive and iterative) and BFS without notes
- [ ] Choose BFS vs DFS vs Union-Find vs topological sort for a new problem, and justify it
- [ ] Explain O(V + E) and why the visited set matters

**Estimated hours:** ~22h

### Self-check interview questions
1. Adjacency list vs adjacency matrix: space, edge lookup, and when to use each?
2. Why does BFS find shortest paths in unweighted graphs, and DFS doesn't?
3. How do you detect a cycle in a directed graph vs an undirected graph?
4. What is a topological order, and when does one exist?
5. Explain Union-Find and its two optimisations.
6. What is multi-source BFS? Give an example.
7. Why use `collections.deque` for BFS in Python?
8. Where do graphs appear in backend systems you know?

---
**Answers**
1. A list takes O(V + E) space and lists neighbours in O(deg), but checking one specific edge costs O(deg). A matrix takes O(V²) space with O(1) edge lookup. Use a list for sparse graphs (most real ones) and a matrix for dense graphs or constant-time edge checks.
2. BFS visits vertices in order of their distance, level by level, so the first time it reaches a vertex is along a shortest path. DFS goes deep first and can reach a vertex by a long path before a short one.
3. Directed: DFS with three states (unvisited / on the current path / done); reaching a node that is still on the current path is a cycle. Kahn's algorithm also works: if not every node gets processed, there is a cycle. Undirected: DFS where you reach a visited node that isn't the parent you came from, or Union-Find where both ends of an edge already share a root.
4. A linear ordering of vertices in which every edge goes from earlier to later. It exists if and only if the graph is a DAG (directed and acyclic).
5. It keeps a forest of sets, and `find` returns a set's root. Path compression points every node on a `find` path straight at the root. Union by rank/size attaches the smaller tree under the larger one. Together they make operations effectively O(α(n)), which is close to constant.
6. BFS started with every source in the queue at distance 0, so each cell gets its distance to the nearest source in a single pass. Examples: rotting oranges, distance to the nearest gate or hospital.
7. `deque.popleft()` is O(1). `list.pop(0)` is O(n) because every remaining element shifts.
8. Dependency graphs (migrations, build steps, task chains), service call graphs, social or follow graphs, routing and maps, permission hierarchies, and detecting cycles in foreign keys or workflows.

## Module 12 — Advanced Graphs (~12h)

**Topics:** weighted graphs, Dijkstra with a min-heap, why negative edges break Dijkstra, Bellman-Ford style relaxation with a limit on edges, minimum spanning trees (Prim, Kruskal), topological sort over derived constraints, Eulerian paths (optional), binary search on the answer combined with graph search.

Prerequisites: Module 9 (heaps), Module 11 (graphs).

### Theory
- [ ] **L12.1 Dijkstra's algorithm** — NeetCode *Advanced Algorithms* → "Dijkstra's"; *Grokking Algorithms* (2nd ed.) Ch. 9 "Dijkstra's algorithm". Trace it by hand on a 5-node weighted graph and write down each heap state.
- [ ] **L12.2 Minimum spanning trees** — NeetCode *Advanced Algorithms* → "Prim's" and "Kruskal's". Explain why both are greedy and why both are correct.
- [ ] **L12.3 Bellman-Ford / relaxation rounds** — what "relax an edge" means, why `k` rounds give the shortest paths that use at most `k` edges, and how negative cycles are detected. NeetCode video "Cheapest Flights Within K Stops".
- [ ] **L12.4 Topological sort revisited** — re-read NeetCode *Advanced* → "Topological Sort" and apply it to constraints you derive yourself (for example, an ordering of letters).
- [ ] **L12.5 Eulerian paths (for the OPTIONAL problem)** — what an Eulerian path is and when one exists (degree conditions). Hierholzer's algorithm at a concept level only.

### Problems

#### 12.1 Find the Town Judge — Easy — Graphs (in/out degree)  [LC 997](https://leetcode.com/problems/find-the-town-judge/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** In a town of `n` people, `trust[i] = [a, b]` means `a` trusts `b`. The judge trusts nobody and is trusted by everyone else. Return the judge's label, or `-1` if there is no judge.
Input: `n = 3`, `trust = [[1,3],[2,3]]` → Output: `3`
**Must be able to explain:**
- [ ] How this maps to in-degree and out-degree
- [ ] Why you don't need an adjacency list
- [ ] Edge case `n = 1` with no trust relationships

#### 12.2 Network Delay Time — Medium — Dijkstra  [LC 743](https://leetcode.com/problems/network-delay-time/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given directed weighted edges `times[i] = [u, v, w]`, `n` nodes and a start node `k`, a signal is sent from `k`. Return how long it takes for every node to receive it, or `-1` if some node never does.
Input: `times = [[2,1,1],[2,3,1],[3,4,1]]`, `n = 4`, `k = 2` → Output: `2`
**Must be able to explain:**
- [ ] Why the answer is the maximum of the shortest distances
- [ ] How "stale" heap entries are handled, and why they appear
- [ ] Time complexity O(E log V), and where the log comes from

#### 12.3 Min Cost to Connect All Points — Medium — MST  [LC 1584](https://leetcode.com/problems/min-cost-to-connect-all-points/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given 2D points, the cost of connecting two points is their Manhattan distance. Return the minimum total cost to connect every point, so that exactly one simple path exists between any two points.
Input: `points = [[0,0],[2,2],[3,10],[5,2],[7,0]]` → Output: `20`
**Must be able to explain:**
- [ ] Why this is a minimum spanning tree problem
- [ ] Prim vs Kruskal on a complete graph, and which one you'd pick
- [ ] Time complexity of your approach

#### 12.4 Cheapest Flights Within K Stops — Medium — Bellman-Ford / BFS  [LC 787](https://leetcode.com/problems/cheapest-flights-within-k-stops/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given `n` cities and flights `[from, to, price]`, return the cheapest price from `src` to `dst` with at most `k` stops, or `-1` if no such route exists.
Input: `n = 4`, `flights = [[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]]`, `src = 0`, `dst = 3`, `k = 1` → Output: `700`
**Must be able to explain:**
- [ ] Why plain Dijkstra can give the wrong answer when stops are limited
- [ ] Why you copy the distance array each round, and the bug if you don't
- [ ] Time complexity in terms of `k` and `E`

#### 12.5 Reconstruct Itinerary — Hard — Eulerian Path  [LC 332](https://leetcode.com/problems/reconstruct-itinerary/)  **OPTIONAL**
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given airline tickets `[from, to]`, rebuild the itinerary in order. It must start at `"JFK"` and use every ticket exactly once. If several itineraries are valid, return the one that is smallest lexically.
Input: `[["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]` → Output: `["JFK","MUC","LHR","SFO","SJC"]`
**Must be able to explain:**
- [ ] Why this is an Eulerian path problem
- [ ] How the "smallest lexical order" rule affects your data structure
- [ ] Why greedily following the smallest destination can get stuck, and how your approach recovers

#### 12.6 Swim in Rising Water — Hard — Dijkstra / Binary Search  [LC 778](https://leetcode.com/problems/swim-in-rising-water/)  **OPTIONAL**
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** In an `n x n` grid, `grid[i][j]` is the elevation. At time `t` you can swim between adjacent cells if both elevations are ≤ `t`. Return the smallest `t` that lets you get from the top-left corner to the bottom-right corner.
Input: `grid = [[0,2],[1,3]]` → Output: `3`
**Must be able to explain:**
- [ ] How the "cost" of a path is defined here (it is not a sum)
- [ ] Two different approaches (modified Dijkstra; binary search on `t` plus a traversal) and their complexities
- [ ] Why binary search on the answer is valid (monotonicity)

#### 12.7 Alien Dictionary — Hard — Topological Sort  [NeetCode](https://neetcode.io/problems/foreign-dictionary) (LC 269, premium)  **OPTIONAL**
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given a list of words sorted lexicographically by an unknown alphabet, return a string of their letters in that alphabet's order. If the order is invalid, return `""`.
Input: `["wrt","wrf","er","ett","rftt"]` → Output: `"wertf"`
**Must be able to explain:**
- [ ] What one pair of adjacent words tells you, and what it doesn't
- [ ] The prefix edge case (`["abc", "ab"]`), and why it is invalid
- [ ] How a contradiction (a cycle) is detected

### Module 12 checklist — must be able to do/explain
- [ ] Implement Dijkstra with `heapq` from a blank file
- [ ] Explain when Dijkstra, BFS, Bellman-Ford or an MST algorithm is the right tool
- [ ] Explain why Dijkstra fails with negative edges
- [ ] Implement Kruskal's using the Union-Find class from Module 11

**Estimated hours:** ~12h

### Self-check interview questions
1. What problem does Dijkstra solve, and what is its complexity with a binary heap?
2. Why doesn't Dijkstra work with negative edge weights?
3. What is a minimum spanning tree? Compare Prim and Kruskal.
4. When would you use Bellman-Ford instead of Dijkstra?
5. What does "relaxing an edge" mean?
6. How does a maps or routing service find shortest paths at scale? Name the ideas, not the code.

---
**Answers**
1. Single-source shortest paths on a graph with non-negative weights. With a binary heap it runs in O((V + E) log V).
2. Dijkstra finalises a node the first time it is popped, assuming no later path can be cheaper. A negative edge found later can break that assumption.
3. An MST is a subset of edges that connects every vertex with minimum total weight and no cycles. Prim grows one tree from a start vertex, taking the cheapest edge out of the tree (heap-based, good for dense graphs). Kruskal sorts all edges and adds each one that doesn't create a cycle, using Union-Find (good for sparse graphs or edge lists).
4. When edges can be negative, when you must detect negative cycles, or when paths are limited to at most `k` edges. It costs O(V·E).
5. For an edge `u → v` with weight `w`: if `dist[u] + w < dist[v]`, set `dist[v] = dist[u] + w`.
6. Precomputation and heuristics: A* with a distance heuristic, bidirectional search, contraction hierarchies, graph partitioning, and caching popular routes. Plain Dijkstra over a whole country is too slow.

---

## Module 13 — 1-D Dynamic Programming (~22h)

**Topics:** overlapping subproblems and optimal substructure, recursion → memoization → tabulation, defining the state and transition, base cases, space optimisation, `functools.cache`, the 0/1 and unbounded knapsack families, palindrome DP, Kadane-style running state.

### Theory
- [ ] **L13.1 What DP is** — NeetCode *Beginners* → "1-Dimension DP"; *Grokking Algorithms* (2nd ed.) Ch. 11 "Dynamic programming". Solve Fibonacci four ways: naive recursion, memo, table, O(1) space.
- [ ] **L13.2 The DP recipe** — write down the state, its meaning in plain words, the transition, the base cases and the answer's location for every problem in this module, **before** coding.
- [ ] **L13.3 Memoization in Python** — `functools.cache` / `lru_cache` ([docs](https://docs.python.org/3/library/functools.html#functools.cache)), hashable arguments, recursion limits.
- [ ] **L13.4 Knapsack families** — NeetCode *Advanced Algorithms* → "0 / 1 Knapsack" and "Unbounded Knapsack".
- [ ] **L13.5 Palindromes** — NeetCode *Advanced Algorithms* → "Palindromes".
- [ ] **L13.6 Kadane's algorithm** — NeetCode *Advanced Algorithms* → "Kadane's Algorithm".

### Problems

#### 13.1 Fibonacci Number — Easy — 1-D DP warm-up  [LC 509](https://leetcode.com/problems/fibonacci-number/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return `F(n)`, where `F(0) = 0`, `F(1) = 1` and `F(n) = F(n-1) + F(n-2)`.
Input: `n = 4` → Output: `3`
**Must be able to explain:**
- [ ] Why naive recursion is O(2ⁿ); draw the tree for `n = 5`
- [ ] The complexity of the memo and table versions
- [ ] How to get O(1) extra space

#### 13.2 N-th Tribonacci Number — Easy — 1-D DP warm-up  [LC 1137](https://leetcode.com/problems/n-th-tribonacci-number/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** `T0 = 0`, `T1 = 1`, `T2 = 1`, and `T(n+3) = T(n) + T(n+1) + T(n+2)`. Return `T(n)`.
Input: `n = 4` → Output: `4`
**Must be able to explain:**
- [ ] The state and the transition in words
- [ ] How many previous values you need to keep
- [ ] Bottom-up vs top-down for this problem

#### 13.3 Climbing Stairs — Easy — 1-D DP  [LC 70](https://leetcode.com/problems/climbing-stairs/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** You climb a staircase of `n` steps, taking 1 or 2 steps at a time. Return the number of distinct ways to reach the top.
Input: `n = 3` → Output: `3`
**Must be able to explain:**
- [ ] Define `dp[i]` in plain words
- [ ] Why the recurrence holds (think about the last step)
- [ ] The connection to 13.1

#### 13.4 Min Cost Climbing Stairs — Easy — 1-D DP  [LC 746](https://leetcode.com/problems/min-cost-climbing-stairs/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** `cost[i]` is what you pay to step on stair `i`. After paying you may climb 1 or 2 steps, and you may start at index 0 or 1. Return the minimum cost to get past the last stair.
Input: `cost = [10, 15, 20]` → Output: `15`
**Must be able to explain:**
- [ ] Where "the top" is relative to the array
- [ ] The base cases, and why there are two
- [ ] Space optimisation

#### 13.5 House Robber — Medium — 1-D DP  [LC 198](https://leetcode.com/problems/house-robber/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Houses in a row hold `nums[i]` money, and you can't rob two adjacent houses. Return the maximum you can rob.
Input: `[2, 7, 9, 3, 1]` → Output: `12`
**Must be able to explain:**
- [ ] The choice at each house, and the recurrence
- [ ] Why greedily taking the largest houses, or every other house, fails (give a counterexample)
- [ ] O(1) space version

#### 13.6 House Robber II — Medium — 1-D DP  [LC 213](https://leetcode.com/problems/house-robber-ii/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Same as 13.5, but the houses form a **circle**, so the first and last houses are adjacent.
Input: `[2, 3, 2]` → Output: `3`
**Must be able to explain:**
- [ ] How the circle reduces to the linear problem
- [ ] The edge case of a single house
- [ ] How you reused your 13.5 solution without copy-pasting it

#### 13.7 Longest Palindromic Substring — Medium — 1-D DP / Two Pointers  [LC 5](https://leetcode.com/problems/longest-palindromic-substring/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the longest substring of `s` that is a palindrome.
Input: `"babad"` → Output: `"bab"` (`"aba"` is also accepted)
**Must be able to explain:**
- [ ] Why checking every substring is O(n³)
- [ ] Your approach's time and space complexity
- [ ] How odd-length and even-length palindromes are both handled

#### 13.8 Palindromic Substrings — Medium — 1-D DP / Two Pointers  [LC 647](https://leetcode.com/problems/palindromic-substrings/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the number of palindromic substrings of `s`. Substrings at different positions count separately.
Input: `"aaa"` → Output: `6`
**Must be able to explain:**
- [ ] How this reuses 13.7's idea
- [ ] Complexity
- [ ] Why the answer for `"aaa"` is 6, listing them

#### 13.9 Decode Ways — Medium — 1-D DP  [LC 91](https://leetcode.com/problems/decode-ways/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** A message of letters `A–Z` was encoded as digits (`A → "1"` … `Z → "26"`). Given a digit string, return how many ways it can be decoded.
Input: `"226"` → Output: `3` (`"BZ"`, `"VF"`, `"BBF"`)
**Must be able to explain:**
- [ ] How `"0"` is handled, and why `"06"` has zero decodings
- [ ] The recurrence and which previous states it depends on
- [ ] Why this is structurally similar to Climbing Stairs

#### 13.10 Coin Change — Medium — 1-D DP (unbounded knapsack)  [LC 322](https://leetcode.com/problems/coin-change/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given coin denominations and an `amount`, return the fewest coins that make up the amount, or `-1` if it can't be made. Each coin can be used any number of times.
Input: `coins = [1, 2, 5]`, `amount = 11` → Output: `3` (5 + 5 + 1)
**Must be able to explain:**
- [ ] A coin set where greedy "largest coin first" gives the wrong answer
- [ ] The state, the transition, and how "impossible" is represented
- [ ] Time complexity O(amount × coins)

#### 13.11 Maximum Product Subarray — Medium — 1-D DP  [LC 152](https://leetcode.com/problems/maximum-product-subarray/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the largest product of any non-empty contiguous subarray.
Input: `[2, 3, -2, 4]` → Output: `6`
**Must be able to explain:**
- [ ] Why tracking only the maximum so far isn't enough
- [ ] How zeros and negative numbers affect the running state
- [ ] How this relates to Kadane's algorithm

#### 13.12 Word Break — Medium — 1-D DP  [LC 139](https://leetcode.com/problems/word-break/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given string `s` and a dictionary `wordDict`, return whether `s` can be split into a sequence of one or more dictionary words (words may be reused).
Input: `s = "leetcode"`, `wordDict = ["leet","code"]` → Output: `true`
**Must be able to explain:**
- [ ] The meaning of `dp[i]` and the direction you fill it
- [ ] Time complexity, including the cost of slicing strings
- [ ] Why plain backtracking without a memo blows up (for example `"aaaa…ab"`)

#### 13.13 Longest Increasing Subsequence — Medium — 1-D DP  [LC 300](https://leetcode.com/problems/longest-increasing-subsequence/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the length of the longest strictly increasing subsequence (not necessarily contiguous).
Input: `[10, 9, 2, 5, 3, 7, 101, 18]` → Output: `4` (for example `[2, 3, 7, 101]`)
**Must be able to explain:**
- [ ] The O(n²) DP: state and transition
- [ ] That an O(n log n) approach exists, and the idea behind it at a high level
- [ ] Subsequence vs substring

#### 13.14 Partition Equal Subset Sum — Medium — 1-D DP (0/1 knapsack)  [LC 416](https://leetcode.com/problems/partition-equal-subset-sum/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return whether the array can be split into two subsets with equal sums.
Input: `[1, 5, 11, 5]` → Output: `true` (`[1, 5, 5]` and `[11]`)
**Must be able to explain:**
- [ ] The quick rejection check before doing any DP
- [ ] How this reduces to a 0/1 knapsack / subset-sum question
- [ ] Why the loop direction matters in the 1-D table version

### Module 13 checklist — must be able to do/explain
- [ ] For any 1-D DP problem, state the state, transition, base cases and answer location in words first
- [ ] Convert a memoized recursion into a bottom-up table, and then into O(1) space when possible
- [ ] Tell 0/1 knapsack from unbounded knapsack
- [ ] Explain why a greedy approach fails on at least two problems in this module

**Estimated hours:** ~22h

### Self-check interview questions
1. What two properties make a problem suitable for DP?
2. Memoization vs tabulation: pros and cons?
3. How do you decide what `dp[i]` should mean?
4. Why is Coin Change DP and not greedy?
5. What is the difference between 0/1 and unbounded knapsack?
6. How do you reduce DP space from O(n) to O(1)?
7. What does `functools.cache` do, and what are its limits?
8. DP vs divide and conquer?

---
**Answers**
1. Overlapping subproblems (the same subproblem is solved many times) and optimal substructure (an optimal answer is built from optimal answers to its subproblems).
2. Memoization (top-down) is easy to write from the recursion and only computes the states it needs, but it pays recursion overhead and depth limits. Tabulation (bottom-up) has no recursion, makes space optimisation easy and is often faster, but you have to get the fill order right.
3. Ask what smallest piece of information about a prefix, suffix or index lets you build the answer for a larger one. Write it in words ("`dp[i]` = the best X using the first `i` items"), then check that the transition only needs earlier states.
4. For arbitrary coin sets, the locally best coin can force a worse total. With coins `{1, 3, 4}` and amount 6, greedy gives 4 + 1 + 1 (3 coins) but the best is 3 + 3 (2 coins). DP tries every last coin.
5. In 0/1 knapsack each item is used at most once. In unbounded knapsack each item can be used any number of times. In a 1-D table this shows up as the iteration direction over capacity.
6. When the transition only reads the last one or two states (or the previous row), keep just those in variables and roll them forward.
7. It stores results keyed by the arguments. Arguments must be hashable, the cache is unbounded (memory), and recursion depth is still limited.
8. Both split a problem into subproblems. Divide and conquer (merge sort) has independent subproblems. DP has overlapping ones, so it caches their results.

---

## Module 14 — Intervals (~9h)

**Topics:** interval representation, overlap conditions, sorting by start vs by end, merging, inserting, counting maximum simultaneous intervals, sweep line, heaps for interval problems.

### Theory
- [ ] **L14.1 Overlap rules** — write the exact condition for "`[a, b]` and `[c, d]` overlap" for closed and half-open intervals. Practise on 10 hand-made pairs.
- [ ] **L14.2 Sorting as the first step** — why almost every interval problem begins with a sort, and what sorting by start vs by end gives you. NeetCode videos: "Merge Intervals", "Non-overlapping Intervals" (neetcode.io/roadmap → Intervals).
- [ ] **L14.3 Scheduling and greedy** — *Grokking Algorithms* (2nd ed.) Ch. 10 "Greedy algorithms" (the classroom scheduling problem).
- [ ] **L14.4 Sweep line and heaps** — turning intervals into start/end events, and connecting back to Module 9 heaps.

### Problems

#### 14.1 Summary Ranges — Easy — Intervals warm-up  [LC 228](https://leetcode.com/problems/summary-ranges/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given a sorted array of unique integers, return the smallest list of ranges that covers every number exactly. Write `"a->b"` for a range and `"a"` for a single number.
Input: `[0, 1, 2, 4, 5, 7]` → Output: `["0->2", "4->5", "7"]`
**Must be able to explain:**
- [ ] How you detect the end of a range
- [ ] Edge cases: empty array, a single element, negative numbers
- [ ] Complexity

#### 14.2 Meeting Rooms — Easy — Intervals  [NeetCode](https://neetcode.io/problems/meeting-schedule) (LC 252, premium)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given meeting time intervals `[start, end]`, return whether one person can attend all of them.
Input: `[[0,30],[5,10],[15,20]]` → Output: `false`
**Must be able to explain:**
- [ ] Why sorting first reduces this to checking adjacent pairs
- [ ] Whether `[1,5]` and `[5,10]` conflict, based on the problem's definition
- [ ] Complexity

#### 14.3 Insert Interval — Medium — Intervals  [LC 57](https://leetcode.com/problems/insert-interval/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given non-overlapping intervals sorted by start, insert `newInterval` and merge where needed so that the list stays sorted and non-overlapping.
Input: `intervals = [[1,3],[6,9]]`, `newInterval = [2,5]` → Output: `[[1,5],[6,9]]`
**Must be able to explain:**
- [ ] The three groups of intervals relative to the new one
- [ ] Why this is O(n) with no sort
- [ ] Edge cases: an empty list, the new interval before all or after all

#### 14.4 Merge Intervals — Medium — Intervals  [LC 56](https://leetcode.com/problems/merge-intervals/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Merge every overlapping interval and return the non-overlapping result.
Input: `[[1,3],[2,6],[8,10],[15,18]]` → Output: `[[1,6],[8,10],[15,18]]`
**Must be able to explain:**
- [ ] Why you sort, and by which key
- [ ] The case where one interval fully contains the next
- [ ] Complexity, and where the O(n log n) comes from

#### 14.5 Non-overlapping Intervals — Medium — Intervals / Greedy  [LC 435](https://leetcode.com/problems/non-overlapping-intervals/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the minimum number of intervals you must remove so that the rest don't overlap. Intervals that only touch at an endpoint don't overlap.
Input: `[[1,2],[2,3],[3,4],[1,3]]` → Output: `1`
**Must be able to explain:**
- [ ] Which interval you keep when two overlap, and why that choice is safe
- [ ] How this relates to "maximum number of non-overlapping intervals"
- [ ] Complexity

#### 14.6 Meeting Rooms II — Medium — Intervals / Heap  [NeetCode](https://neetcode.io/problems/meeting-schedule-ii) (LC 253, premium)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given meeting intervals, return the minimum number of conference rooms needed.
Input: `[[0,30],[5,10],[15,20]]` → Output: `2`
**Must be able to explain:**
- [ ] Two approaches (heap of end times; sorted start/end sweep) and their complexities
- [ ] What the heap holds at any moment
- [ ] A backend analogy: peak concurrent connections or jobs

#### 14.7 Minimum Interval to Include Each Query — Hard — Intervals / Heap  [LC 1851](https://leetcode.com/problems/minimum-interval-to-include-each-query/)  **OPTIONAL**
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given `intervals[i] = [left, right]` and `queries`, the answer to `queries[j]` is the size (`right - left + 1`) of the smallest interval containing that query, or `-1` if none does. Return every answer in the original query order.
Input: `intervals = [[1,4],[2,4],[3,6],[4,4]]`, `queries = [2,3,4,5]` → Output: `[3,3,1,4]`
**Must be able to explain:**
- [ ] Why answering each query independently is O(n·q)
- [ ] Why processing queries offline (in sorted order) helps, and how you keep the original order
- [ ] How intervals that no longer contain the query are discarded

### Module 14 checklist — must be able to do/explain
- [ ] Write the overlap condition without hesitating
- [ ] Merge and insert intervals from a blank file
- [ ] Explain when to sort by start vs by end
- [ ] Solve "max simultaneous intervals" in two different ways

**Estimated hours:** ~9h

### Self-check interview questions
1. When do two intervals `[a, b]` and `[c, d]` overlap?
2. Why do interval problems usually begin with sorting?
3. In interval scheduling, why sort by end time?
4. How do you compute the maximum number of overlapping intervals?
5. Where do interval problems appear in backend work?

---
**Answers**
1. For closed intervals: `a <= d and c <= b`. For half-open intervals `[a, b)`: `a < d and c < b`. Whether touching counts is always part of the problem definition.
2. After sorting, any interval that can overlap the current one comes right after it, so one linear pass is enough and pairwise O(n²) checks are avoided.
3. Keeping the interval that ends earliest leaves the most room for the rest. An exchange argument shows this choice is never worse than any other.
4. Either turn intervals into +1/−1 events, sort them and track a running sum (the sweep line), or sort by start and keep a min-heap of end times. The largest heap size is the answer.
5. Booking and double-booking checks (appointments, rooms), rate-limit windows, time-series gaps, merging maintenance windows, IP/range allocation, and Postgres range types with `EXCLUDE` constraints.

---

## Module 15 — Greedy (~12h)

**Topics:** the greedy choice property, local vs global optimum, exchange-argument proofs, counterexamples where greedy fails, reachability / "furthest so far" scans, frequency-driven greedy, Kadane's algorithm.

### Theory
- [ ] **L15.1 Greedy algorithms** — *Grokking Algorithms* (2nd ed.) Ch. 10 "Greedy algorithms" (classroom scheduling, knapsack, set covering, and when greedy is only approximate).
- [ ] **L15.2 Proving a greedy step** — the informal exchange argument: "take an optimal solution that differs from mine, and swap in my choice without making it worse". Try it on 14.5.
- [ ] **L15.3 Kadane revisited** — NeetCode *Advanced Algorithms* → "Kadane's Algorithm".
- [ ] **L15.4 When greedy fails** — collect 3 counterexamples (Coin Change 13.10, House Robber 13.5, 0/1 knapsack) in your notes.
- [ ] NeetCode videos: neetcode.io/roadmap → Greedy (watch only after attempting each problem).

### Problems

#### 15.1 Assign Cookies — Easy — Greedy warm-up  [LC 455](https://leetcode.com/problems/assign-cookies/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Child `i` is content with a cookie of size ≥ `g[i]`. Cookie `j` has size `s[j]`. Each child gets at most one cookie. Return the maximum number of content children.
Input: `g = [1, 2, 3]`, `s = [1, 1]` → Output: `1`
**Must be able to explain:**
- [ ] The greedy choice, and why it is safe
- [ ] Complexity
- [ ] A variant where greedy would fail, if you can think of one

#### 15.2 Maximum Subarray — Medium — Greedy / Kadane  [LC 53](https://leetcode.com/problems/maximum-subarray/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the largest sum of any non-empty contiguous subarray.
Input: `[-2, 1, -3, 4, -1, 2, 1, -5, 4]` → Output: `6` (`[4, -1, 2, 1]`)
**Must be able to explain:**
- [ ] The decision made at each index
- [ ] The all-negative array edge case
- [ ] How you would also return the start and end indices

#### 15.3 Jump Game — Medium — Greedy  [LC 55](https://leetcode.com/problems/jump-game/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** `nums[i]` is the maximum jump length from index `i`. Starting at index 0, return whether you can reach the last index.
Input: `[2, 3, 1, 1, 4]` → Output: `true`; `[3, 2, 1, 0, 4]` → Output: `false`
**Must be able to explain:**
- [ ] The DP solution and why it is O(n²)
- [ ] The O(n) greedy idea, and what single value it tracks
- [ ] Why the second example fails

#### 15.4 Jump Game II — Medium — Greedy  [LC 45](https://leetcode.com/problems/jump-game-ii/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Same setup, but the last index is guaranteed reachable. Return the minimum number of jumps.
Input: `[2, 3, 1, 1, 4]` → Output: `2`
**Must be able to explain:**
- [ ] The connection to BFS levels
- [ ] When the jump counter increases
- [ ] Complexity

#### 15.5 Gas Station — Medium — Greedy  [LC 134](https://leetcode.com/problems/gas-station/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** On a circular route, station `i` gives `gas[i]` and driving to the next station costs `cost[i]`. Return the starting station that lets you complete the loop once, or `-1` if none does (the answer is unique if it exists).
Input: `gas = [1,2,3,4,5]`, `cost = [3,4,5,1,2]` → Output: `3`
**Must be able to explain:**
- [ ] The global condition for whether any answer exists
- [ ] Why, when you fail at station `j`, no station between the start and `j` can be the answer
- [ ] O(n) vs brute-force O(n²)

#### 15.6 Hand of Straights — Medium — Greedy  [LC 846](https://leetcode.com/problems/hand-of-straights/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return whether the cards in `hand` can be rearranged into groups of `groupSize` consecutive values.
Input: `hand = [1,2,3,6,2,3,4,7,8]`, `groupSize = 3` → Output: `true` (`[1,2,3]`, `[2,3,4]`, `[6,7,8]`)
**Must be able to explain:**
- [ ] Which card must start a group, and why
- [ ] The data structures you used, and the complexity
- [ ] The quick rejection check

#### 15.7 Merge Triplets to Form Target Triplet — Medium — Greedy  [LC 1899](https://leetcode.com/problems/merge-triplets-to-form-target-triplet/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Merging two triplets means taking the element-wise max. Return whether some sequence of merges over the given triplets can produce `target` exactly.
Input: `triplets = [[2,5,3],[1,8,4],[1,7,5]]`, `target = [2,7,5]` → Output: `true`
**Must be able to explain:**
- [ ] Which triplets can never be used, and why
- [ ] What must be true of the usable ones for the answer to be yes
- [ ] Complexity

#### 15.8 Partition Labels — Medium — Greedy  [LC 763](https://leetcode.com/problems/partition-labels/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Split `s` into as many parts as possible so that each letter appears in at most one part. Return the sizes of the parts.
Input: `"ababcbacadefegdehijhklij"` → Output: `[9, 7, 8]`
**Must be able to explain:**
- [ ] What precomputation you do and why
- [ ] When a part can be closed
- [ ] Complexity, given the alphabet is fixed

#### 15.9 Valid Parenthesis String — Medium — Greedy  [LC 678](https://leetcode.com/problems/valid-parenthesis-string/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** `s` contains `(`, `)` and `*`, where `*` can be `(`, `)` or empty. Return whether `s` can be valid.
Input: `"(*))"` → Output: `true`
**Must be able to explain:**
- [ ] Why the simple stack/counter from Valid Parentheses isn't enough
- [ ] A DP or two-stack approach vs the greedy range approach, with complexities
- [ ] The invariant your greedy keeps

### Module 15 checklist — must be able to do/explain
- [ ] Recognise when a problem has a greedy structure, and give a counterexample when it doesn't
- [ ] Sketch an exchange argument for at least one problem
- [ ] Solve Jump Game both with DP and greedily, and compare them

**Estimated hours:** ~12h

### Self-check interview questions
1. What is a greedy algorithm?
2. How do you convince an interviewer that your greedy solution is correct?
3. Give a problem where greedy fails, and explain why.
4. Greedy vs DP: how do you decide which to use?
5. Explain Kadane's algorithm in two sentences.
6. Name a greedy algorithm used in real systems.

---
**Answers**
1. It makes the locally best choice at each step and never revisits it, hoping to reach a global optimum. That only works when the problem has the greedy-choice property.
2. With an exchange argument (any optimal solution can be changed into yours without getting worse), an invariant that holds after every step, or at least by trying to build a counterexample and failing.
3. Coin Change with `{1, 3, 4}` and amount 6: greedy gives 3 coins, the optimum is 2. The first greedy choice (4) removes the optimal path.
4. If you can prove a single local choice is always safe, use greedy. If a choice depends on how later subproblems turn out, you need DP. Try a small counterexample first.
5. Walk the array keeping the best sum of a subarray that ends at the current index: extend the previous subarray or start fresh at the current element. The answer is the maximum of those values.
6. Dijkstra, Prim/Kruskal for MSTs, Huffman coding (compression), interval scheduling / booking, and load balancers sending work to the least-loaded node.

## Module 16 — 2-D Dynamic Programming (~20h)

**Topics:** 2-D states on grids and on pairs of strings or sequences, fill order, "state machine" DP (holding / not holding / cooldown), counting vs optimising DP, rolling-row space optimisation, DFS + memoization on grids, interval DP (optional).

Prerequisites: Module 13.

### Theory
- [ ] **L16.1 2-D DP** — NeetCode *Beginners* → "2-Dimension DP". Fill a 3×4 Unique Paths table by hand.
- [ ] **L16.2 Longest Common Subsequence** — NeetCode *Advanced Algorithms* → "LCS"; *Grokking Algorithms* (2nd ed.) Ch. 11 (the grid method, longest common substring vs subsequence).
- [ ] **L16.3 State-machine DP** — model a problem as states plus transitions (for example "holding a stock" / "not holding" / "cooling down") and draw the diagram before building a table.
- [ ] **L16.4 Counting vs optimising** — the same table with `+` instead of `min`/`max`, and why loop order changes what gets counted (combinations vs permutations).
- [ ] **L16.5 Space optimisation** — reduce an `m x n` table to one or two rows, and what that costs you if you later need to reconstruct the path.

### Problems

#### 16.1 Pascal's Triangle — Easy — 2-D DP warm-up  [LC 118](https://leetcode.com/problems/pascals-triangle/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the first `numRows` rows of Pascal's triangle.
Input: `numRows = 5` → Output: `[[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]]`
**Must be able to explain:**
- [ ] How each row depends on the previous one
- [ ] Why this is a DP table
- [ ] Time and space complexity

#### 16.2 Unique Paths — Medium — 2-D DP  [LC 62](https://leetcode.com/problems/unique-paths/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** A robot on an `m x n` grid starts at the top-left corner and can move only right or down. Return the number of unique paths to the bottom-right corner.
Input: `m = 3`, `n = 7` → Output: `28`
**Must be able to explain:**
- [ ] The state, the transition and the base row/column
- [ ] O(n) space version
- [ ] The combinatorics formula, and why it gives the same answer

#### 16.3 Longest Common Subsequence — Medium — 2-D DP  [LC 1143](https://leetcode.com/problems/longest-common-subsequence/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the length of the longest subsequence the two strings share, or 0 if they share none.
Input: `text1 = "abcde"`, `text2 = "ace"` → Output: `3`
**Must be able to explain:**
- [ ] What `dp[i][j]` means, and the two cases of the transition
- [ ] How to reconstruct the actual subsequence from the table
- [ ] Where LCS shows up in practice (`diff`, version control)

#### 16.4 Best Time to Buy and Sell Stock with Cooldown — Medium — 2-D DP (state machine)  [LC 309](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given daily prices, return the maximum profit. You may make any number of transactions, but you can't hold more than one share, and after a sale you must wait one day before buying again.
Input: `[1, 2, 3, 0, 2]` → Output: `3` (buy, sell, cooldown, buy, sell)
**Must be able to explain:**
- [ ] The states and the allowed transitions (draw them)
- [ ] Why this is "2-D" even if you store it in a few variables
- [ ] Complexity

#### 16.5 Coin Change II — Medium — 2-D DP (unbounded knapsack, counting)  [LC 518](https://leetcode.com/problems/coin-change-ii/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the number of **combinations** of coins that make up `amount`, using each coin any number of times.
Input: `amount = 5`, `coins = [1, 2, 5]` → Output: `4`
**Must be able to explain:**
- [ ] Why `1+2+2` and `2+1+2` must count once, and how your loop order ensures that
- [ ] How this differs from 13.10 (Coin Change)
- [ ] 2-D table vs 1-D table version

#### 16.6 Target Sum — Medium — 2-D DP  [LC 494](https://leetcode.com/problems/target-sum/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Put `+` or `-` in front of every number in `nums`. Return how many ways the expression evaluates to `target`.
Input: `nums = [1, 1, 1, 1, 1]`, `target = 3` → Output: `5`
**Must be able to explain:**
- [ ] The brute-force O(2ⁿ) tree, and where subproblems overlap
- [ ] The memo key you use
- [ ] That a subset-sum reformulation exists, and why it works (high level)

#### 16.7 Interleaving String — Medium — 2-D DP  [LC 97](https://leetcode.com/problems/interleaving-string/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return whether `s3` is an interleaving of `s1` and `s2` that keeps the relative order of characters within each.
Input: `s1 = "aabcc"`, `s2 = "dbbca"`, `s3 = "aadbbcbcac"` → Output: `true`
**Must be able to explain:**
- [ ] The quick length check
- [ ] What `dp[i][j]` represents, and why the index into `s3` isn't a third dimension
- [ ] Why a two-pointer greedy fails

#### 16.8 Edit Distance — Medium — 2-D DP  [LC 72](https://leetcode.com/problems/edit-distance/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the minimum number of insert, delete and replace operations needed to turn `word1` into `word2`.
Input: `word1 = "horse"`, `word2 = "ros"` → Output: `3`
**Must be able to explain:**
- [ ] What each of the three operations means as a move in the table
- [ ] The base row and base column
- [ ] Real uses: spell checking, fuzzy search (Elasticsearch fuzziness), DNA alignment

#### 16.9 Longest Increasing Path in a Matrix — Hard — DFS + Memoization  [LC 329](https://leetcode.com/problems/longest-increasing-path-in-a-matrix/)  **OPTIONAL**
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the length of the longest strictly increasing path in a matrix, moving up, down, left or right.
Input: `[[9,9,4],[6,6,8],[2,1,1]]` → Output: `4` (`1 → 2 → 6 → 9`)
**Must be able to explain:**
- [ ] Why no visited set is needed along a path
- [ ] Why the memo makes it O(m·n)
- [ ] The alternative view as the longest path in a DAG (topological order)

#### 16.10 Distinct Subsequences — Hard — 2-D DP  [LC 115](https://leetcode.com/problems/distinct-subsequences/)  **OPTIONAL**
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the number of distinct subsequences of `s` that equal `t`.
Input: `s = "rabbbit"`, `t = "rabbit"` → Output: `3`
**Must be able to explain:**
- [ ] The two choices when characters match, and the one choice when they don't
- [ ] Base cases (an empty `t`, an empty `s`)
- [ ] Complexity and space optimisation

#### 16.11 Burst Balloons — Hard — 2-D DP (interval DP)  [LC 312](https://leetcode.com/problems/burst-balloons/)  **OPTIONAL**
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Each balloon has a number. Bursting balloon `i` earns `left * nums[i] * right`, where `left` and `right` are its current neighbours (out-of-bounds counts as 1). Return the maximum coins from bursting every balloon.
Input: `[3, 1, 5, 8]` → Output: `167`
**Must be able to explain:**
- [ ] Why "which balloon do I burst first?" leads to a dead end
- [ ] The reframing that makes the subproblems independent
- [ ] Why the complexity is O(n³)

#### 16.12 Regular Expression Matching — Hard — 2-D DP  [LC 10](https://leetcode.com/problems/regular-expression-matching/)  **OPTIONAL**
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Implement matching for patterns with `.` (any one character) and `*` (zero or more of the preceding element). The pattern must match the **whole** string.
Input: `s = "aa"`, `p = "a*"` → Output: `true`; `s = "aa"`, `p = "a"` → Output: `false`
**Must be able to explain:**
- [ ] The two choices `x*` gives you
- [ ] Why patterns like `a*b*c*` against an empty string need careful base cases
- [ ] Complexity, and how Python's `re` differs (backtracking engine, catastrophic backtracking)

### Module 16 checklist — must be able to do/explain
- [ ] Define 2-D states over (index, index) and (row, col) in words before coding
- [ ] Build LCS and Edit Distance tables by hand for small inputs
- [ ] Explain combination-vs-permutation counting and how loop order controls it
- [ ] Reduce a 2-D table to rolling rows

**Estimated hours:** ~20h

### Self-check interview questions
1. How do you recognise that a problem needs a 2-D DP state?
2. Explain the LCS recurrence.
3. Why is the loop order important in Coin Change II?
4. What is a state-machine DP? Give an example.
5. How do you reconstruct the actual answer, not just its value, from a DP table?
6. What is the time and space complexity of Edit Distance, and can the space be reduced?
7. Where does edit distance show up in backend systems?

---
**Answers**
1. The subproblem depends on two changing parameters: positions in two strings, (row, col) in a grid, (index, remaining capacity), or (index, state).
2. `dp[i][j]` is the LCS length of `text1[:i]` and `text2[:j]`. If the last characters match, it is `dp[i-1][j-1] + 1`. Otherwise it is `max(dp[i-1][j], dp[i][j-1])`.
3. Looping over coins on the outside and amounts on the inside counts each combination once. The other order counts ordered sequences (permutations).
4. DP whose state includes a discrete "mode" with allowed transitions between modes. Example: the stock problems with holding / sold / cooldown.
5. Keep the full table (or parent pointers), then walk backwards from the answer cell, following whichever transition produced each value.
6. O(m·n) time and O(m·n) space. Space drops to O(min(m, n)) with two rows, but you lose the easy reconstruction of the edits.
7. Fuzzy search and "did you mean", deduplicating names or addresses, diffs, and similarity scoring in search engines (Elasticsearch's `fuzziness` uses Levenshtein distance).

---

## Module 17 — Bit Manipulation (~8h)

**Topics:** binary representation, two's complement, bitwise operators (`&`, `|`, `^`, `~`, `<<`, `>>`), XOR properties, testing/setting/clearing bit `k`, `n & (n - 1)`, bit counting, Python's unbounded integers and 32-bit emulation.

### Theory
- [ ] **L17.1 Bit operations** — NeetCode *Beginners* → "Bit Operations".
- [ ] **L17.2 Python specifics** — [Bitwise operations on integer types](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types), `int.bit_count()`, `bin()`, `format(x, "032b")`. Python ints are unbounded: what that means for problems that assume 32-bit integers.
- [ ] **L17.3 XOR properties** — `x ^ x = 0`, `x ^ 0 = x`, commutative and associative. Prove each one on paper with 4-bit numbers.
- [ ] **L17.4 Two's complement** — how `-5` is stored in 8 bits, and why `~x == -x - 1`.

### Problems

#### 17.1 Power of Two — Easy — Bit warm-up  [LC 231](https://leetcode.com/problems/power-of-two/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return whether integer `n` is a power of two.
Input: `n = 16` → Output: `true`; `n = 3` → Output: `false`
**Must be able to explain:**
- [ ] What the binary form of a power of two looks like
- [ ] A loop solution vs an O(1) bit solution
- [ ] Edge cases: `0` and negative numbers

#### 17.2 Single Number — Easy — Bit  [LC 136](https://leetcode.com/problems/single-number/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Every element appears twice except one. Find that one in O(n) time and O(1) extra space.
Input: `[4, 1, 2, 1, 2]` → Output: `4`
**Must be able to explain:**
- [ ] Which XOR properties make this work
- [ ] Why a hash set solution doesn't meet the space requirement
- [ ] What breaks if an element appears three times

#### 17.3 Number of 1 Bits — Easy — Bit  [LC 191](https://leetcode.com/problems/number-of-1-bits/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the number of set bits in the binary form of a positive integer (its Hamming weight).
Input: `n = 11` (binary `1011`) → Output: `3`
**Must be able to explain:**
- [ ] A shift-and-mask loop, and its iteration count
- [ ] The `n & (n - 1)` trick, and why its loop runs only once per set bit
- [ ] The Python built-in, and when you'd use it in production code

#### 17.4 Counting Bits — Easy — Bit / DP  [LC 338](https://leetcode.com/problems/counting-bits/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** For every `i` in `0..n`, return the number of `1` bits in `i`.
Input: `n = 5` → Output: `[0, 1, 1, 2, 1, 2]`
**Must be able to explain:**
- [ ] The O(n log n) approach using 17.3
- [ ] How earlier answers can be reused (the DP relationship)
- [ ] Complexity of the O(n) version

#### 17.5 Reverse Bits — Easy — Bit  [LC 190](https://leetcode.com/problems/reverse-bits/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Reverse the bits of a 32-bit unsigned integer.
Input: `43261596` (`00000010100101000001111010011100`) → Output: `964176192` (`00111001011110000010100101000000`)
**Must be able to explain:**
- [ ] How you read bit `i` and write it to position `31 - i`
- [ ] Why it is always exactly 32 iterations
- [ ] How you'd speed it up if it were called millions of times (for example a lookup table per byte)

#### 17.6 Missing Number — Easy — Bit / Math  [LC 268](https://leetcode.com/problems/missing-number/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** `nums` holds `n` distinct numbers from `0..n`. Return the one missing number.
Input: `[3, 0, 1]` → Output: `2`
**Must be able to explain:**
- [ ] Three approaches (set, math formula, XOR) and their space
- [ ] Why the math version has no overflow risk in Python but would in Java or C
- [ ] Why the XOR version works

#### 17.7 Sum of Two Integers — Medium — Bit  [LC 371](https://leetcode.com/problems/sum-of-two-integers/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return `a + b` without using the `+` or `-` operators.
Input: `a = 1`, `b = 2` → Output: `3`
**Must be able to explain:**
- [ ] Which operation gives the "sum without carry", and which gives the "carry"
- [ ] Why negative numbers make the Python version loop forever without extra care, and how you prevent it
- [ ] How many iterations are needed at most for 32-bit numbers

#### 17.8 Reverse Integer — Medium — Math / Bit  [LC 7](https://leetcode.com/problems/reverse-integer/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Reverse the digits of a signed 32-bit integer. If the result falls outside `[-2³¹, 2³¹ - 1]`, return 0. Assume you can't store 64-bit integers.
Input: `123` → Output: `321`; `-123` → Output: `-321`; `120` → Output: `21`
**Must be able to explain:**
- [ ] How Python's `%` and `//` behave with negative numbers, and why that matters here
- [ ] How you detect overflow **before** it happens
- [ ] Why converting to a string is acceptable in Python but misses the point of the question

### Module 17 checklist — must be able to do/explain
- [ ] Test, set, clear and toggle bit `k` without looking anything up
- [ ] Explain two's complement and Python's unbounded integers
- [ ] Use XOR properties to cancel pairs
- [ ] Explain what `n & (n - 1)` does

**Estimated hours:** ~8h

### Self-check interview questions
1. How do you check whether bit `k` of `x` is set? How do you set it and clear it?
2. What does `n & (n - 1)` do?
3. Why does XOR find the unique element when all the others appear twice?
4. How are negative numbers represented in binary (two's complement)?
5. How are Python integers different from C/Java integers for bit problems?
6. Where are bit operations used in real backends?

---
**Answers**
1. Test: `(x >> k) & 1`, or `x & (1 << k) != 0`. Set: `x | (1 << k)`. Clear: `x & ~(1 << k)`. Toggle: `x ^ (1 << k)`.
2. It clears the lowest set bit. It is useful for counting set bits and for checking powers of two (`n > 0 and n & (n - 1) == 0`).
3. XOR is commutative and associative, `a ^ a = 0` and `a ^ 0 = a`. Every pair cancels out and only the unique value is left.
4. Invert every bit of the positive value and add 1. The top bit is the sign. This makes addition and subtraction the same hardware operation.
5. Python ints have arbitrary precision, so there is no overflow and `-1` has infinitely many leading 1 bits. To emulate 32-bit behaviour you mask with `0xFFFFFFFF` and convert back to signed yourself.
6. Permission and feature flags packed into bitmasks, Bloom filters, bitmap indexes (Postgres bitmap heap scans), hashing (consistent hashing, CRC), Redis `SETBIT`/`BITCOUNT` for analytics, network masks (CIDR), and compact encodings (varints in Protobuf).

---

## Module 18 — Math & Geometry (~11h)

**Topics:** digit manipulation with `divmod`, integer overflow awareness, cycle detection on number sequences, matrix traversal and in-place transforms (transpose, reflect, layer by layer), fast exponentiation, grade-school arithmetic on digit strings, counting geometric shapes with hash maps.

### Theory
- [ ] **L18.1 Digits and arithmetic** — `divmod`, `%` with negatives in Python, reversing and summing digits. Python docs: [`divmod`](https://docs.python.org/3/library/functions.html#divmod), [`math`](https://docs.python.org/3/library/math.html).
- [ ] **L18.2 Matrix traversal** — row/column indices, boundaries, layers, and in-place transforms. Draw a 4×4 matrix and write down the index mapping for "transpose" and "reflect horizontally".
- [ ] **L18.3 Fast exponentiation** — computing `xⁿ` in O(log n) multiplications, and how it relates to binary representation (Module 17).
- [ ] **L18.4 Cycle detection revisited** — re-read Floyd's fast/slow pointers from Module 6 (NeetCode *Advanced* → "Fast and Slow Pointers") and apply it to sequences of numbers.
- [ ] NeetCode videos: neetcode.io/roadmap → Math & Geometry.

### Problems

#### 18.1 Palindrome Number — Easy — Math warm-up  [LC 9](https://leetcode.com/problems/palindrome-number/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return whether integer `x` reads the same backwards as forwards, **without** converting it to a string.
Input: `121` → Output: `true`; `-121` → Output: `false`
**Must be able to explain:**
- [ ] Why negative numbers and numbers ending in 0 (other than 0 itself) are rejected quickly
- [ ] How to reverse only half the number, and why that avoids overflow
- [ ] Complexity in terms of the number of digits

#### 18.2 Transpose Matrix — Easy — Matrix warm-up  [LC 867](https://leetcode.com/problems/transpose-matrix/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return the transpose of a matrix (flip it over its main diagonal).
Input: `[[1,2,3],[4,5,6]]` → Output: `[[1,4],[2,5],[3,6]]`
**Must be able to explain:**
- [ ] The index mapping
- [ ] Why a non-square matrix can't be transposed in place
- [ ] What `zip(*matrix)` does, and whether it is fair to use in an interview

#### 18.3 Happy Number — Easy — Math / Hashing  [LC 202](https://leetcode.com/problems/happy-number/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Repeatedly replace `n` with the sum of the squares of its digits. `n` is happy if the process reaches 1. Otherwise it loops forever. Return whether `n` is happy.
Input: `19` → Output: `true` (1² + 9² = 82 → 68 → 100 → 1)
**Must be able to explain:**
- [ ] Why the sequence must either reach 1 or cycle
- [ ] The hash-set approach vs the O(1)-space approach
- [ ] The link to Linked List Cycle

#### 18.4 Plus One — Easy — Math  [LC 66](https://leetcode.com/problems/plus-one/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** A non-negative integer is stored as an array of digits, most significant first. Add one and return the resulting array.
Input: `[9, 9]` → Output: `[1, 0, 0]`
**Must be able to explain:**
- [ ] How the carry propagates
- [ ] When the array has to grow
- [ ] Complexity

#### 18.5 Rotate Image — Medium — Matrix  [LC 48](https://leetcode.com/problems/rotate-image/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Rotate an `n x n` matrix 90° clockwise **in place**.
Input: `[[1,2,3],[4,5,6],[7,8,9]]` → Output: `[[7,4,1],[8,5,2],[9,6,3]]`
**Must be able to explain:**
- [ ] Two different in-place strategies at a high level (layer-by-layer swaps; composing simpler transforms)
- [ ] The index mapping for a 90° clockwise rotation
- [ ] How you'd rotate counter-clockwise

#### 18.6 Spiral Matrix — Medium — Matrix  [LC 54](https://leetcode.com/problems/spiral-matrix/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Return every element of an `m x n` matrix in spiral order (clockwise from the top-left corner).
Input: `[[1,2,3],[4,5,6],[7,8,9]]` → Output: `[1,2,3,6,9,8,7,4,5]`
**Must be able to explain:**
- [ ] Which boundaries you track, and when each one moves
- [ ] How you avoid adding elements twice in a single row or column
- [ ] Complexity

#### 18.7 Set Matrix Zeroes — Medium — Matrix  [LC 73](https://leetcode.com/problems/set-matrix-zeroes/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** If an element is 0, set its whole row and column to 0, in place.
Input: `[[1,1,1],[1,0,1],[1,1,1]]` → Output: `[[1,0,1],[0,0,0],[1,0,1]]`
**Must be able to explain:**
- [ ] Why zeroing as you scan gives wrong results
- [ ] The O(m + n) space solution
- [ ] How O(1) extra space is possible, and the special case it needs

#### 18.8 Pow(x, n) — Medium — Math / Binary Exponentiation  [LC 50](https://leetcode.com/problems/powx-n/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Implement `x` raised to the power `n` (where `n` may be negative) without `**` or `pow`.
Input: `x = 2.0`, `n = 10` → Output: `1024.0`; `x = 2.0`, `n = -2` → Output: `0.25`
**Must be able to explain:**
- [ ] Why multiplying `n` times is too slow for `n = 2³¹ - 1`
- [ ] How the number of multiplications becomes O(log n)
- [ ] How negative exponents and `n = -2³¹` are handled

#### 18.9 Multiply Strings — Medium — Math  [LC 43](https://leetcode.com/problems/multiply-strings/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Given two non-negative integers as strings, return their product as a string, without converting the whole strings to integers.
Input: `"123"`, `"456"` → Output: `"56088"`
**Must be able to explain:**
- [ ] Where the product of digit `i` and digit `j` lands in the result
- [ ] The maximum length of the result, and why
- [ ] Leading-zero and `"0"` edge cases

#### 18.10 Detect Squares — Medium — Math / Hashing  [LC 2013](https://leetcode.com/problems/detect-squares/)
- [ ] Solved  · [ ] R1 · [ ] R3 · [ ] R7
**Problem:** Design `DetectSquares` with `add(point)` (duplicate points allowed) and `count(point)`, which returns how many ways you can choose three stored points that form, together with the query point, an axis-aligned square of positive area.
Input: `add([3,10])`, `add([11,2])`, `add([3,2])`, `count([11,10])`, `count([14,8])`, `add([11,2])`, `count([11,10])` → Output: `1, 0, 2`
**Must be able to explain:**
- [ ] Which point you fix first, and what that determines about the other corners
- [ ] How duplicate points affect the count
- [ ] The complexity of `add` and `count`

### Module 18 checklist — must be able to do/explain
- [ ] Manipulate digits with `divmod` and reason about overflow as if you had 32-bit integers
- [ ] Traverse and transform matrices in place, from a blank file
- [ ] Explain fast exponentiation
- [ ] Spot "this is secretly cycle detection"

**Estimated hours:** ~11h

### Self-check interview questions
1. How does Python's `%` behave with negative numbers, compared with C/Java?
2. Explain fast exponentiation and its complexity.
3. How do you rotate a square matrix 90° in place?
4. How do you detect a cycle in a sequence without extra memory?
5. How would you add two huge numbers given as strings?
6. Why can floating-point arithmetic be dangerous (think money), and what do you use instead?

---
**Answers**
1. Python's `%` takes the sign of the divisor (`-7 % 3 == 1`) and `//` floors (`-7 // 3 == -3`). C and Java truncate towards zero (`-7 / 3 == -2`, `-7 % 3 == -1`). This matters when you reverse digits or convert between languages.
2. Square the base and halve the exponent at each step, multiplying the result in whenever the current exponent is odd (that is, for each set bit of `n`). It takes O(log n) multiplications.
3. For example, transpose and then reverse every row, or rotate four cells at a time layer by layer. Both are O(n²) time and O(1) extra space.
4. Floyd's tortoise and hare: advance one pointer by 1 and the other by 2. If they meet, there is a cycle. Detecting that the sequence reached a fixed end (like 1 in Happy Number) ends the loop.
5. Walk both strings from the right, add digit by digit with a carry, collect the digits and reverse them at the end. It is O(max(m, n)).
6. Binary floats can't represent most decimal fractions exactly (`0.1 + 0.2 != 0.3`), and rounding errors pile up. For money, use integer minor units (cents) or `decimal.Decimal` with explicit rounding rules.

---

## Track 1B progress summary

| Module | Topic | Problems | NeetCode 150 | Done |
|---|---|---|---|---|
| 0 | Foundations | 12 | 0 | 0 |
| 1 | Arrays & Hashing | 12 | 9 | 6 |
| 2 | Two Pointers | 8 | 5 | 0 |
| 3 | Sliding Window | 8 | 6 | 0 |
| 4 | Stack | 9 | 7 | 0 |
| 5 | Binary Search | 9 | 7 | 0 |
| 6 | Linked List | 14 | 11 | 0 |
| 7 | Trees | 19 | 15 | 0 |
| 8 | Tries | 4 | 3 | 0 |
| 9 | Heap / Priority Queue | 9 | 7 | 0 |
| 10 | Backtracking | 10 | 9 | 0 |
| 11 | Graphs | 15 | 13 | 0 |
| 12 | Advanced Graphs | 7 | 6 | 0 |
| 13 | 1-D DP | 14 | 12 | 0 |
| 14 | Intervals | 7 | 6 | 0 |
| 15 | Greedy | 9 | 8 | 0 |
| 16 | 2-D DP | 12 | 11 | 0 |
| 17 | Bit Manipulation | 8 | 7 | 0 |
| 18 | Math & Geometry | 10 | 8 | 0 |
| **Total** | | **196** | **150** | **6** |

Update the **Done** column when you tick a problem's "Solved" box.

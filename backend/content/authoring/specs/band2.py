"""Levels 11-25: medium -> hard midpoint. Stacks/queues, linked lists, windows,
sorting, binary search, recursion, trees, heaps.

5-7 tests per question, exactly 2 visible.
"""

import random

from model import Q, T
from specs.helpers import arr_case, gen_arr, rand_ints

QUESTIONS = [
    # ---------------- L11 (medium, stacks-queues) ----------------
    Q(
        qid="L11-A",
        level=11,
        topic="stacks-queues",
        title="Bracket Wards",
        time_limit_s=4,
        prompt="""
The vault door is sealed by a chain of paired wards: (), [], {}. The chain holds
only if every ward opens and closes in proper nested order.

Input: one line of 1..10^5 characters from ()[]{}.
Output: YES if the sequence is balanced, else NO.
""",
        solution=r"""
import sys
s = sys.stdin.read().strip()
pairs = {')': '(', ']': '[', '}': '{'}
stack = []
ok = True
for c in s:
    if c in '([{':
        stack.append(c)
    else:
        if not stack or stack.pop() != pairs[c]:
            ok = False
            break
print("YES" if ok and not stack else "NO")
""",
        tests=[
            T(stdin="([]{})\n", visible=True),
            T(stdin="([)]\n", visible=True),
            T(stdin="]\n", probe="edge:unbalanced"),
            T(stdin="(\n", probe="edge:single"),
            T(gen=lambda rng: "(" * 50000 + ")" * 50000 + "\n", probe="perf:large_n"),
            T(stdin="{[()()]}[\n", probe="adversarial:worst-case"),
        ],
    ),
    Q(
        qid="L11-B",
        level=11,
        topic="stacks-queues",
        title="Next Beacon",
        time_limit_s=5,
        prompt="""
From each watchtower you can see the NEXT taller beacon to your right. For every
tower, report that beacon's height, or -1 if no taller beacon follows.

Input: line 1: n (1 <= n <= 10^5). Line 2: n heights (1 <= h <= 10^9).
Output: n integers on one line. (Hint: a monotonic stack does this in O(n).)
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
vals = list(map(int, data[1:1 + n]))
ans = [-1] * n
stack = []
for i, v in enumerate(vals):
    while stack and vals[stack[-1]] < v:
        ans[stack.pop()] = v
    stack.append(i)
print(" ".join(map(str, ans)))
""",
        tests=[
            T(stdin="4\n2 1 2 4\n", visible=True),
            T(stdin="5\n1 3 2 5 4\n", visible=True),
            T(stdin="4\n9 7 5 3\n", probe="edge:reverse-sorted"),
            T(stdin="4\n1 2 3 4\n", probe="edge:sorted"),
            T(stdin="3\n6 6 6\n", probe="edge:all-equal"),
            T(gen=gen_arr(100000, 1, 10**9), probe="perf:large_n"),
        ],
    ),
    # ---------------- L12 (medium, stacks-queues) ----------------
    Q(
        qid="L12-A",
        level=12,
        topic="stacks-queues",
        title="Runic Abacus",
        time_limit_s=4,
        prompt="""
The dwarven abacus takes commands in reverse polish notation: numbers push, and
+ - * / combine the top two beads. Division truncates toward zero.

Input: line 1: n (1 <= n <= 10^5). Line 2: n tokens (integers or + - * /),
forming a valid RPN expression. Intermediate values fit in 64 bits.
Output: the final value.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
tokens = data[1:1 + n]
stack = []
for tok in tokens:
    if tok in '+-*/' and len(tok) == 1:
        b = stack.pop()
        a = stack.pop()
        if tok == '+':
            stack.append(a + b)
        elif tok == '-':
            stack.append(a - b)
        elif tok == '*':
            stack.append(a * b)
        else:
            q = abs(a) // abs(b)
            stack.append(q if (a >= 0) == (b >= 0) else -q)
    else:
        stack.append(int(tok))
print(stack[0])
""",
        tests=[
            T(stdin="5\n2 3 + 4 *\n", visible=True),
            T(stdin="3\n10 3 /\n", visible=True),
            T(stdin="3\n-7 2 /\n", probe="edge:negative"),
            T(stdin="1\n42\n", probe="edge:single"),
            T(
                gen=lambda rng: (lambda ops: f"{len(ops)}\n{' '.join(ops)}\n")(
                    ["1"] + [tok for _ in range(40000) for tok in (str(rng.randint(1, 9)), "+")]
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L12-B",
        level=12,
        topic="stacks-queues",
        title="Collapse the Sigils",
        time_limit_s=4,
        prompt="""
Adjacent identical sigils annihilate each other, and the wall keeps collapsing
until no adjacent pair matches. What remains?

Input: one line of 1..10^5 lowercase letters.
Output: the remaining string, or EMPTY if everything annihilates.
""",
        solution=r"""
import sys
s = sys.stdin.read().strip()
stack = []
for c in s:
    if stack and stack[-1] == c:
        stack.pop()
    else:
        stack.append(c)
print("".join(stack) if stack else "EMPTY")
""",
        tests=[
            T(stdin="abbaca\n", visible=True),
            T(stdin="azxxzy\n", visible=True),
            T(stdin="abba\n", probe="edge:empty"),
            T(stdin="abcdef\n", probe="edge:no-solution"),
            T(gen=lambda rng: "ab" * 50000 + "\n", probe="perf:large_n"),
        ],
    ),
    # ---------------- L13 (medium, linked-lists) ----------------
    Q(
        qid="L13-A",
        level=13,
        topic="linked-lists",
        title="Chain Reversal",
        prompt="""
The prisoners' chain must be re-shackled: reverse every consecutive group of k
links. If fewer than k links remain at the end, leave that tail unchanged.

Input: line 1: n and k (1 <= k <= n <= 10^5). Line 2: n integers (the chain,
head first).
Output: the re-shackled chain, space-separated.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
vals = data[2:2 + n]
out = []
i = 0
while i + k <= n:
    out.extend(reversed(vals[i:i + k]))
    i += k
out.extend(vals[i:])
print(" ".join(out))
""",
        tests=[
            T(stdin="5 2\n1 2 3 4 5\n", visible=True),
            T(stdin="6 3\n1 2 3 4 5 6\n", visible=True),
            T(stdin="4 1\n8 6 7 5\n", probe="edge:single"),
            T(stdin="4 4\n1 2 3 4\n", probe="edge:max-bounds"),
            T(stdin="5 3\n1 2 3 4 5\n", probe="edge:unbalanced"),
        ],
    ),
    Q(
        qid="L13-B",
        level=13,
        topic="linked-lists",
        title="Ouroboros Check",
        prompt="""
Each cell of the serpent temple has one exit passage (or none). Starting from
cell 0, does the path eventually bite its own tail?

Input: line 1: n (1 <= n <= 10^5). Line 2: n integers next[i] (-1 means no exit,
otherwise 0 <= next[i] < n). You start at cell 0.
Output: YES if the walk from cell 0 revisits a cell, else NO.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
nxt = list(map(int, data[1:1 + n]))
seen = set()
cur = 0
ans = "NO"
while cur != -1:
    if cur in seen:
        ans = "YES"
        break
    seen.add(cur)
    cur = nxt[cur]
print(ans)
""",
        tests=[
            T(stdin="4\n1 2 3 1\n", visible=True),
            T(stdin="3\n1 2 -1\n", visible=True),
            T(stdin="1\n0\n", probe="edge:cycle"),
            T(stdin="5\n1 2 3 4 -1\n", probe="edge:no-solution"),
            T(stdin="6\n1 2 3 4 5 2\n", probe="adversarial:worst-case"),
        ],
    ),
    # ---------------- L14 (medium, sliding-window / hashing) ----------------
    Q(
        qid="L14-A",
        level=14,
        topic="sliding-window",
        title="Watchtower Sweep",
        time_limit_s=4,
        prompt="""
A patrol always guards k CONSECUTIVE watchtowers. Place it where the towers'
combined signal strength is greatest and report that strength.

Input: line 1: n and k (1 <= k <= n <= 10^5). Line 2: n integers, |v| <= 10^6.
Output: the maximum sum over any window of k consecutive values.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
vals = list(map(int, data[2:2 + n]))
window = sum(vals[:k])
best = window
for i in range(k, n):
    window += vals[i] - vals[i - k]
    best = max(best, window)
print(best)
""",
        tests=[
            T(stdin="6 3\n2 1 5 1 3 2\n", visible=True),
            T(stdin="4 2\n4 -1 -2 5\n", visible=True),
            T(stdin="3 3\n1 2 3\n", probe="edge:max-bounds"),
            T(stdin="5 2\n-5 -2 -9 -1 -4\n", probe="edge:negative"),
            T(gen=lambda rng: arr_case(rand_ints(rng, 100000, -10**6, 10**6)).replace("\n", " 500\n", 1), probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L14-B",
        level=14,
        topic="hashing",
        title="Exact Offering",
        time_limit_s=4,
        prompt="""
The altar accepts an offering of consecutive relics whose values sum EXACTLY to
the demanded amount. Count how many such consecutive runs exist. Values may be
negative - cursed relics subtract.

Input: line 1: n and demand (1 <= n <= 10^5, |demand| <= 10^9). Line 2: n
integers, |v| <= 10^4.
Output: the number of contiguous subarrays summing to demand.
""",
        solution=r"""
import sys
from collections import defaultdict
data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
vals = list(map(int, data[2:2 + n]))
seen = defaultdict(int)
seen[0] = 1
prefix = 0
count = 0
for v in vals:
    prefix += v
    count += seen[prefix - k]
    seen[prefix] += 1
print(count)
""",
        tests=[
            T(stdin="5 5\n1 2 3 2 3\n", visible=True),
            T(stdin="3 3\n1 1 1\n", visible=True),
            T(stdin="5 0\n0 0 0 0 0\n", probe="edge:zero"),
            T(stdin="6 2\n3 -1 4 -2 -2 4\n", probe="edge:negative"),
            T(gen=lambda rng: arr_case(rand_ints(rng, 100000, -100, 100)).replace("\n", " 7\n", 1), probe="perf:large_n"),
        ],
    ),
    # ---------------- L15 BOSS (medium, stacks-queues) ----------------
    Q(
        qid="L15-B1",
        level=15,
        topic="stacks-queues",
        title="Sentinel of Colder Days",
        is_boss=True,
        time_limit_s=5,
        prompt="""
BOSS. The Sentinel records the dungeon's temperature each day. For every day,
it demands to know how many days one must wait for a STRICTLY warmer day - or
0 if no warmer day ever comes.

Input: line 1: n (1 <= n <= 10^5). Line 2: n temperatures (-10^6 <= t <= 10^6).
Output: n integers on one line. (An O(n^2) scan will freeze to death.)
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
temps = list(map(int, data[1:1 + n]))
ans = [0] * n
stack = []
for i, t in enumerate(temps):
    while stack and temps[stack[-1]] < t:
        j = stack.pop()
        ans[j] = i - j
    stack.append(i)
print(" ".join(map(str, ans)))
""",
        tests=[
            T(stdin="8\n73 74 75 71 69 72 76 73\n", visible=True),
            T(stdin="4\n30 40 50 60\n", visible=True),
            T(stdin="5\n90 80 70 60 50\n", probe="edge:reverse-sorted"),
            T(stdin="4\n55 55 55 55\n", probe="edge:all-equal"),
            T(gen=lambda rng: arr_case([(i % 2) and 10 or 20 for i in range(100000)]), probe="adversarial:worst-case"),
            T(gen=gen_arr(100000, -1000000, 1000000), probe="perf:large_n"),
        ],
    ),
    # ---------------- L16 (medium, sorting) ----------------
    Q(
        qid="L16-A",
        level=16,
        topic="sorting",
        title="Union of Hosts",
        time_limit_s=5,
        prompt="""
Two allied hosts march in sorted order of soldier rank. Merge them into a single
sorted column without breaking stride.

Input: line 1: n and m (0 <= n, m <= 10^5, n+m >= 1). Line 2: n sorted integers
(omitted if n=0). Line 3: m sorted integers (omitted if m=0).
Output: the n+m values merged in non-decreasing order, space-separated.
""",
        solution=r"""
import sys
import heapq
data = sys.stdin.read().split()
n, m = int(data[0]), int(data[1])
a = list(map(int, data[2:2 + n]))
b = list(map(int, data[2 + n:2 + n + m]))
print(" ".join(map(str, list(heapq.merge(a, b)))))
""",
        tests=[
            T(stdin="3 3\n1 3 5\n2 4 6\n", visible=True),
            T(stdin="2 3\n10 20\n1 2 30\n", visible=True),
            T(stdin="0 3\n4 5 6\n", probe="edge:empty"),
            T(stdin="3 3\n2 2 2\n2 2 2\n", probe="edge:duplicates"),
            T(
                gen=lambda rng: (lambda a, b: f"{len(a)} {len(b)}\n{' '.join(map(str, a))}\n{' '.join(map(str, b))}\n")(
                    sorted(rand_ints(rng, 100000, -10**9, 10**9)), sorted(rand_ints(rng, 100000, -10**9, 10**9))
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L16-B",
        level=16,
        topic="sorting",
        title="K-th Gem",
        time_limit_s=4,
        prompt="""
The dragon sorts its gems by size before sleeping on them. Which gem ends up in
position k of the sorted hoard?

Input: line 1: n and k (1 <= k <= n <= 10^5). Line 2: n gem sizes, |v| <= 10^9.
Output: the k-th smallest value (1-based).
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
vals = sorted(map(int, data[2:2 + n]))
print(vals[k - 1])
""",
        tests=[
            T(stdin="5 2\n7 10 4 3 20\n", visible=True),
            T(stdin="4 4\n1 9 2 8\n", visible=True),
            T(stdin="3 1\n5 2 8\n", probe="edge:single"),
            T(stdin="4 4\n6 6 1 6\n", probe="edge:duplicates"),
            T(gen=lambda rng: arr_case(rand_ints(rng, 100000, -10**9, 10**9)).replace("\n", " 50000\n", 1), probe="perf:large_n"),
        ],
    ),
    # ---------------- L17 (medium, binary-search) ----------------
    Q(
        qid="L17-A",
        level=17,
        topic="binary-search",
        title="First Light",
        time_limit_s=4,
        prompt="""
The candles along the great stair are sorted by brightness. Find the FIRST candle
of exactly the brightness you seek.

Input: line 1: n and target (1 <= n <= 10^5). Line 2: n integers in non-decreasing
order, |v| <= 10^9.
Output: the smallest 1-based index holding target, or -1 if absent. (Linear scans
gutter out; binary search.)
""",
        solution=r"""
import sys
from bisect import bisect_left
data = sys.stdin.read().split()
n, target = int(data[0]), int(data[1])
vals = list(map(int, data[2:2 + n]))
i = bisect_left(vals, target)
print(i + 1 if i < n and vals[i] == target else -1)
""",
        tests=[
            T(stdin="6 5\n1 3 5 5 5 9\n", visible=True),
            T(stdin="4 2\n1 3 5 7\n", visible=True),
            T(stdin="5 10\n1 2 3 4 5\n", probe="edge:no-solution"),
            T(stdin="4 4\n4 4 4 4\n", probe="edge:all-equal"),
            T(
                gen=lambda rng: (lambda vals: arr_case(vals).replace("\n", f" {vals[70000]}\n", 1))(
                    sorted(rand_ints(rng, 100000, -10**9, 10**9))
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L17-B",
        level=17,
        topic="binary-search",
        title="Root of the Mountain",
        prompt="""
The mountain's heart lies at a depth equal to the integer square root of its
mass: the greatest integer r with r*r <= N.

Input: one integer N (0 <= N <= 10^18).
Output: floor(sqrt(N)). (Floating point will betray you near the top.)
""",
        solution=r"""
import sys
import math
n = int(sys.stdin.read())
print(math.isqrt(n))
""",
        tests=[
            T(stdin="16\n", visible=True),
            T(stdin="26\n", visible=True),
            T(stdin="1\n", probe="edge:single"),
            T(stdin="999999999999999999\n", probe="edge:overflow"),
            T(stdin="1000000000000000000\n", probe="edge:max-bounds"),
        ],
    ),
    # ---------------- L18 (medium, recursion) ----------------
    Q(
        qid="L18-A",
        level=18,
        topic="recursion",
        title="Coffer Combinations",
        time_limit_s=5,
        prompt="""
You may take any subset of the n treasures, but the coffer's curse demands the
loot weigh EXACTLY w. Count the subsets that satisfy the curse. (The empty
subset counts only when w = 0.)

Input: line 1: n and w (1 <= n <= 20, 0 <= w <= 10^9). Line 2: n positive
weights, each <= 10^8.
Output: the number of qualifying subsets.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n, w = int(data[0]), int(data[1])
vals = list(map(int, data[2:2 + n]))

def count(i, remaining):
    if remaining == 0 and i == n:
        return 1
    if i == n:
        return 0
    total = count(i + 1, remaining)
    if vals[i] <= remaining:
        total += count(i + 1, remaining - vals[i])
    return total

sys.setrecursionlimit(100)
print(count(0, w))
""",
        tests=[
            T(stdin="4 6\n1 2 3 4\n", visible=True),
            T(stdin="3 7\n2 2 3\n", visible=True),
            T(stdin="3 100\n1 2 3\n", probe="edge:no-solution"),
            T(stdin="4 10\n1 2 3 4\n", probe="edge:max-bounds"),
            T(gen=lambda rng: f"20 50\n{' '.join(str(rng.randint(1, 10)) for _ in range(20))}\n", probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L18-B",
        level=18,
        topic="recursion",
        title="Stairs of the Spire",
        time_limit_s=4,
        prompt="""
The spire's staircase has n steps; your boots allow strides of 1 or 2 steps.
Count the distinct ways to reach the top, modulo 1000000007.

Input: one integer n (1 <= n <= 10^6).
Output: the number of ways mod 1000000007. (Naive recursion dies at the 40th
step; memoize or iterate.)
""",
        solution=r"""
import sys
MOD = 1000000007
n = int(sys.stdin.read())
a, b = 1, 1
for _ in range(n):
    a, b = b, (a + b) % MOD
print(a)
""",
        tests=[
            T(stdin="4\n", visible=True),
            T(stdin="10\n", visible=True),
            T(stdin="1\n", probe="edge:single"),
            T(stdin="50\n", probe="edge:overflow"),
            T(stdin="1000000\n", probe="perf:large_n"),
        ],
    ),
    # ---------------- L19 (medium, greedy/sorting) ----------------
    Q(
        qid="L19-A",
        level=19,
        topic="greedy",
        title="War Tents",
        time_limit_s=4,
        prompt="""
Each war council occupies a tent from time s to time e (it vacates exactly at e,
so a council starting at e may reuse the same tent). What is the fewest tents
that houses all n councils?

Input: line 1: n (1 <= n <= 10^5). Then n lines "s e" (0 <= s < e <= 10^9).
Output: the minimum number of tents.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
events = []
idx = 1
for _ in range(n):
    s, e = int(data[idx]), int(data[idx + 1])
    idx += 2
    events.append((s, 1))
    events.append((e, -1))
events.sort()
cur = best = 0
for _, delta in events:
    cur += delta
    best = max(best, cur)
print(best)
""",
        tests=[
            T(stdin="3\n0 30\n5 10\n15 20\n", visible=True),
            T(stdin="2\n7 10\n2 4\n", visible=True),
            T(stdin="3\n1 10\n2 9\n3 8\n", probe="edge:max-bounds"),
            T(stdin="3\n1 5\n5 9\n9 12\n", probe="adversarial:worst-case"),
            T(
                gen=lambda rng: f"100000\n" + "".join(
                    (lambda s: f"{s} {s + rng.randint(1, 1000)}\n")(rng.randint(0, 10**9 - 1001)) for _ in range(100000)
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L19-B",
        level=19,
        topic="sorting",
        title="Scroll Shelving",
        time_limit_s=4,
        prompt="""
The librarian shelves scrolls by title length, shortest first; equal lengths go
alphabetically. Print the shelving order.

Input: line 1: n (1 <= n <= 10^5). Then n lines, each a lowercase title of
1..30 letters.
Output: the n titles in shelving order, one per line.
""",
        solution=r"""
import sys
lines = sys.stdin.read().split()
n = int(lines[0])
titles = lines[1:1 + n]
titles.sort(key=lambda t: (len(t), t))
print("\n".join(titles))
""",
        tests=[
            T(stdin="4\nember\nash\ntorch\nowl\n", visible=True),
            T(stdin="3\nbat\ncat\nant\n", visible=True),
            T(stdin="3\nrune\nrune\nrune\n", probe="edge:duplicates"),
            T(stdin="1\nzephyr\n", probe="edge:single"),
            T(
                gen=lambda rng: f"100000\n" + "".join(
                    "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(rng.randint(1, 30))) + "\n"
                    for _ in range(100000)
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L20 BOSS (medium-hard, binary-search) ----------------
    Q(
        qid="L20-B1",
        level=20,
        topic="binary-search",
        title="Ferryman's Bargain",
        is_boss=True,
        time_limit_s=5,
        prompt="""
BOSS. The Ferryman grants you h hours to burn n rope coils. Each hour you pick
ONE coil and burn up to s lengths of it (a coil shorter than s still consumes
the whole hour). Name the smallest burning speed s that clears every coil in
time.

Input: line 1: n and h (1 <= n <= 10^5, n <= h <= 10^9). Line 2: n coil lengths
(1 <= len <= 10^9).
Output: the minimum integer speed s. (Binary search the answer.)
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n, h = int(data[0]), int(data[1])
piles = list(map(int, data[2:2 + n]))

def hours(speed):
    return sum((p + speed - 1) // speed for p in piles)

lo, hi = 1, max(piles)
while lo < hi:
    mid = (lo + hi) // 2
    if hours(mid) <= h:
        hi = mid
    else:
        lo = mid + 1
print(lo)
""",
        tests=[
            T(stdin="4 8\n3 6 7 11\n", visible=True),
            T(stdin="3 6\n30 11 23\n", visible=True),
            T(stdin="4 4\n5 9 2 14\n", probe="edge:max-bounds"),
            T(stdin="1 3\n10\n", probe="edge:single"),
            T(stdin="3 1000000000\n1000000000 1000000000 1000000000\n", probe="edge:overflow"),
            T(gen=lambda rng: arr_case(rand_ints(rng, 100000, 1, 10**9)).replace("\n", " 150000\n", 1), probe="perf:large_n"),
        ],
    ),
    # ---------------- L21 (medium-hard, trees) ----------------
    Q(
        qid="L21-A",
        level=21,
        topic="trees",
        title="Depth of the Root Cellar",
        time_limit_s=4,
        prompt="""
The root cellar grows as a binary tree, given in level order where N marks a
missing branch. How many levels deep does it reach?

Input: line 1: m (1 <= m <= 2*10^5) - the number of tokens. Line 2: m tokens,
level order: integers or N.
Output: the maximum depth (a single node is depth 1).
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.read().split()
m = int(data[0])
tokens = data[1:1 + m]
if not tokens or tokens[0] == 'N':
    print(0)
else:
    depth = [1]
    queue = deque([(0, 1)])
    idx = 1
    best = 1
    while queue and idx < m:
        node, d = queue.popleft()
        for _ in range(2):
            if idx >= m:
                break
            tok = tokens[idx]
            idx += 1
            if tok != 'N':
                best = max(best, d + 1)
                queue.append((idx - 1, d + 1))
    print(best)
""",
        tests=[
            T(stdin="7\n3 9 20 N N 15 7\n", visible=True),
            T(stdin="5\n1 2 N 3 N\n", visible=True),
            T(stdin="1\n7\n", probe="edge:single"),
            T(stdin="15\n1 2 3 4 5 6 7 8 9 10 11 12 13 14 15\n", probe="edge:max-bounds"),
            T(
                gen=lambda rng: (lambda toks: f"{len(toks)}\n{' '.join(toks)}\n")(
                    [tok for i in range(3000) for tok in (str(i + 1), 'N')][:-1]
                ),
                probe="edge:unbalanced",
            ),
        ],
    ),
    Q(
        qid="L21-B",
        level=21,
        topic="trees",
        title="Heaviest Corridor",
        time_limit_s=4,
        prompt="""
Each level of the fortress tree stores treasure in its nodes. Find the level
(1-based, root = level 1) with the greatest total; on a tie report the
shallowest.

Input: line 1: m. Line 2: m level-order tokens (integers or N for missing),
|value| <= 10^6, at most 2*10^5 tokens.
Output: the 1-based level with the maximum sum.
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.read().split()
m = int(data[0])
tokens = data[1:1 + m]
sums = {}
queue = deque()
if tokens and tokens[0] != 'N':
    queue.append((int(tokens[0]), 1))
idx = 1
while queue:
    val, d = queue.popleft()
    sums[d] = sums.get(d, 0) + val
    for _ in range(2):
        if idx < m:
            tok = tokens[idx]
            idx += 1
            if tok != 'N':
                queue.append((int(tok), d + 1))
best = min(sums.items(), key=lambda kv: (-kv[1], kv[0]))
print(best[0])
""",
        tests=[
            T(stdin="7\n1 7 0 7 -8 N N\n", visible=True),
            T(stdin="3\n50 6 2\n", visible=True),
            T(stdin="7\n1 -2 -3 4 5 6 7\n", probe="edge:negative"),
            T(stdin="1\n99\n", probe="edge:single"),
            T(
                gen=lambda rng: (lambda toks: f"{len(toks)}\n{' '.join(toks)}\n")(
                    [tok for i in range(3000) for tok in (str(rng.randint(-100, 100)), 'N')][:-1]
                ),
                probe="edge:unbalanced",
            ),
        ],
    ),
    # ---------------- L22 (medium-hard, trees) ----------------
    Q(
        qid="L22-A",
        level=22,
        topic="trees",
        title="Covenant of Order",
        time_limit_s=4,
        prompt="""
A true covenant tree keeps every left descendant strictly smaller and every
right descendant strictly larger than its ancestor - at EVERY depth, not just
parent-child. Verify the covenant.

Input: line 1: m. Line 2: m level-order tokens (integers or N), at most
2*10^5 tokens, values fit in 64 bits.
Output: YES if the tree is a strict binary search tree, else NO.
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.read().split()
m = int(data[0])
tokens = data[1:1 + m]
nodes = []
for tok in tokens:
    nodes.append(None if tok == 'N' else int(tok))
left = {}
right = {}
queue = deque()
if nodes and nodes[0] is not None:
    queue.append(0)
idx = 1
while queue:
    node = queue.popleft()
    for side in (left, right):
        if idx < m:
            if nodes[idx] is not None:
                side[node] = idx
                queue.append(idx)
            idx += 1

def valid():
    stack = [(0, float('-inf'), float('inf'))] if nodes and nodes[0] is not None else []
    while stack:
        i, lo, hi = stack.pop()
        v = nodes[i]
        if not (lo < v < hi):
            return False
        if i in left:
            stack.append((left[i], lo, v))
        if i in right:
            stack.append((right[i], v, hi))
    return True

print("YES" if valid() else "NO")
""",
        tests=[
            T(stdin="3\n2 1 3\n", visible=True),
            T(stdin="7\n5 1 7 N N 6 8\n", visible=True),
            T(stdin="3\n5 5 6\n", probe="edge:duplicates"),
            T(stdin="7\n10 5 15 N N 6 20\n", probe="adversarial:worst-case"),
            T(stdin="1\n42\n", probe="edge:single"),
            T(
                gen=lambda rng: (lambda toks: f"{len(toks)}\n{' '.join(toks)}\n")(
                    [tok for i in range(3000) for tok in (str(10**9 - i), 'N')][:-1]
                ),
                probe="edge:sorted",
            ),
        ],
    ),
    Q(
        qid="L22-B",
        level=22,
        topic="trees",
        title="Eldest Common Ancestor",
        time_limit_s=4,
        prompt="""
In the ancestral covenant tree (a strict BST), two heirs dispute their lineage.
Name the eldest ancestor both share - the deepest node whose bloodline contains
both values.

Input: line 1: m, then line 2: m level-order tokens of a valid BST. Line 3: two
values a and b, both guaranteed present.
Output: the value of the lowest common ancestor.
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.read().split()
m = int(data[0])
tokens = data[1:1 + m]
a, b = int(data[1 + m]), int(data[2 + m])
nodes = [None if t == 'N' else int(t) for t in tokens]
left = {}
right = {}
queue = deque([0]) if nodes and nodes[0] is not None else deque()
idx = 1
while queue:
    node = queue.popleft()
    for side in (left, right):
        if idx < m:
            if nodes[idx] is not None:
                side[node] = idx
                queue.append(idx)
            idx += 1
lo, hi = min(a, b), max(a, b)
cur = 0
while True:
    v = nodes[cur]
    if hi < v:
        cur = left[cur]
    elif lo > v:
        cur = right[cur]
    else:
        print(v)
        break
""",
        tests=[
            T(stdin="7\n6 2 8 0 4 7 9\n2 8\n", visible=True),
            T(stdin="7\n6 2 8 0 4 7 9\n0 4\n", visible=True),
            T(stdin="7\n6 2 8 0 4 7 9\n2 4\n", probe="adversarial:worst-case"),
            T(stdin="2\n5 1\n1 5\n", probe="edge:single"),
            T(
                gen=lambda rng: (lambda toks: f"{len(toks)}\n{' '.join(toks)}\n1 {len(toks) // 2 + 1}\n")(
                    [tok for i in range(2000) for tok in (str(i + 1), 'N') if not (i > 0 and tok == 'N' and False)][
                        : 2 * 2000 - 1
                    ]
                ),
                probe="edge:sorted",
            ),
        ],
    ),
    # ---------------- L23 (medium-hard, heaps) ----------------
    Q(
        qid="L23-A",
        level=23,
        topic="heaps",
        title="Crown of Embers",
        time_limit_s=4,
        prompt="""
Only the k hottest embers may crown the forge. Report them from hottest to
coolest.

Input: line 1: n and k (1 <= k <= n <= 10^5). Line 2: n temperatures,
|v| <= 10^9.
Output: the k largest values in non-increasing order, space-separated.
""",
        solution=r"""
import sys
import heapq
data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
vals = list(map(int, data[2:2 + n]))
print(" ".join(map(str, heapq.nlargest(k, vals))))
""",
        tests=[
            T(stdin="6 3\n5 1 9 3 7 2\n", visible=True),
            T(stdin="4 1\n4 8 1 6\n", visible=True),
            T(stdin="3 3\n2 9 2\n", probe="edge:max-bounds"),
            T(stdin="5 2\n7 7 7 7 7\n", probe="edge:duplicates"),
            T(gen=lambda rng: arr_case(rand_ints(rng, 100000, -10**9, 10**9)).replace("\n", " 100\n", 1), probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L23-B",
        level=23,
        topic="heaps",
        title="Confluence of Streams",
        time_limit_s=5,
        prompt="""
k underground streams, each already sorted, meet in one channel. Emit the merged
flow in sorted order.

Input: line 1: k (1 <= k <= 100). Then k lines; each starts with a length
len_i (0 <= len_i <= 2000) followed by len_i sorted integers. Total values
<= 10^5.
Output: all values merged in non-decreasing order (guaranteed at least one).
""",
        solution=r"""
import sys
import heapq
data = sys.stdin.read().split()
k = int(data[0])
idx = 1
streams = []
for _ in range(k):
    ln = int(data[idx])
    idx += 1
    streams.append(list(map(int, data[idx:idx + ln])))
    idx += ln
print(" ".join(map(str, heapq.merge(*streams))))
""",
        tests=[
            T(stdin="3\n3 1 4 5\n3 1 3 4\n2 2 6\n", visible=True),
            T(stdin="2\n2 1 10\n2 2 20\n", visible=True),
            T(stdin="3\n0\n2 3 9\n0\n", probe="edge:empty"),
            T(stdin="4\n1 5\n1 1\n1 9\n1 3\n", probe="edge:single"),
            T(
                gen=lambda rng: "50\n" + "".join(
                    (lambda vals: f"{len(vals)} {' '.join(map(str, vals))}\n")(sorted(rand_ints(rng, 2000, -10**6, 10**6)))
                    for _ in range(50)
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L24 (medium-hard, trees) ----------------
    Q(
        qid="L24-A",
        level=24,
        topic="trees",
        title="Span of the World Tree",
        time_limit_s=4,
        prompt="""
The World Tree's span is the number of branches on the longest path between ANY
two of its nodes - the path need not pass the root.

Input: line 1: m. Line 2: m level-order tokens (integers or N), at most
2*10^5 tokens.
Output: the diameter counted in edges.
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.read().split()
m = int(data[0])
tokens = data[1:1 + m]
nodes = [None if t == 'N' else int(t) for t in tokens]
left = {}
right = {}
queue = deque([0]) if nodes and nodes[0] is not None else deque()
idx = 1
while queue:
    node = queue.popleft()
    for side in (left, right):
        if idx < m:
            if nodes[idx] is not None:
                side[node] = idx
                queue.append(idx)
            idx += 1

best = 0
depth = {}
order = []
stack = [0] if nodes and nodes[0] is not None else []
while stack:
    i = stack.pop()
    order.append(i)
    for child_map in (left, right):
        if i in child_map:
            stack.append(child_map[i])
for i in reversed(order):
    dl = depth.get(left.get(i, -1), 0)
    dr = depth.get(right.get(i, -1), 0)
    depth[i] = 1 + max(dl, dr)
    best = max(best, dl + dr)
print(best)
""",
        tests=[
            T(stdin="5\n1 2 3 4 5\n", visible=True),
            T(stdin="1\n1\n", visible=True),
            T(
                stdin="15\n1 2 N 3 N 4 N 5 N 6 N 7 N 8 N\n",
                probe="edge:unbalanced",
            ),
            T(stdin="13\n1 2 3 4 N N 5 6 N N 7 8 9\n", probe="adversarial:worst-case"),
            T(stdin="3\n9 4 6\n", probe="edge:single"),
        ],
    ),
    Q(
        qid="L24-B",
        level=24,
        topic="trees",
        title="Serpent's Procession",
        time_limit_s=4,
        prompt="""
The temple serpent reads each level of the tree in alternating direction: level 1
left-to-right, level 2 right-to-left, and so on. Transcribe its procession.

Input: line 1: m. Line 2: m level-order tokens (integers or N), at most
2*10^5 tokens, root present.
Output: one line per level, values space-separated in serpent order.
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.read().split()
m = int(data[0])
tokens = data[1:1 + m]
nodes = [None if t == 'N' else int(t) for t in tokens]
children = {}
queue = deque([(0, 1)])
idx = 1
levels = {}
while queue:
    i, d = queue.popleft()
    levels.setdefault(d, []).append(nodes[i])
    for _ in range(2):
        if idx < m:
            if nodes[idx] is not None:
                queue.append((idx, d + 1))
            idx += 1
out = []
for d in sorted(levels):
    row = levels[d]
    if d % 2 == 0:
        row = row[::-1]
    out.append(" ".join(map(str, row)))
print("\n".join(out))
""",
        tests=[
            T(stdin="7\n3 9 20 N N 15 7\n", visible=True),
            T(stdin="3\n1 2 3\n", visible=True),
            T(stdin="1\n5\n", probe="edge:single"),
            T(stdin="15\n1 2 3 4 5 6 7 8 9 10 11 12 13 14 15\n", probe="edge:max-bounds"),
            T(
                stdin="9\n1 2 N 3 N 4 N 5 N\n",
                probe="edge:unbalanced",
            ),
        ],
    ),
    # ---------------- L25 BOSS (hard, dynamic-programming) ----------------
    Q(
        qid="L25-B1",
        level=25,
        topic="dynamic-programming",
        title="Keeper of the Ascending Path",
        is_boss=True,
        time_limit_s=5,
        prompt="""
BOSS - THE MIDPOINT. The Keeper unrolls the map of all n shrines. You may visit
any subsequence of shrines in the given order, but each visited shrine must sit
STRICTLY higher than the last. How long can the pilgrimage be?

Input: line 1: n (1 <= n <= 10^5). Line 2: n altitudes, |v| <= 10^9.
Output: the length of the longest strictly increasing subsequence. (O(n^2) will
not survive the Keeper's patience: use patience sorting / binary search.)
""",
        solution=r"""
import sys
from bisect import bisect_left
data = sys.stdin.read().split()
n = int(data[0])
vals = list(map(int, data[1:1 + n]))
tails = []
for v in vals:
    i = bisect_left(tails, v)
    if i == len(tails):
        tails.append(v)
    else:
        tails[i] = v
print(len(tails))
""",
        tests=[
            T(stdin="8\n10 9 2 5 3 7 101 18\n", visible=True),
            T(stdin="6\n1 2 3 2 3 4\n", visible=True),
            T(stdin="5\n9 8 7 6 5\n", probe="edge:reverse-sorted"),
            T(stdin="4\n4 4 4 4\n", probe="edge:all-equal"),
            T(stdin="5\n1 2 3 4 5\n", probe="edge:sorted"),
            T(stdin="8\n2 2 3 3 4 4 5 5\n", probe="edge:duplicates"),
            T(gen=gen_arr(100000, -10**9, 10**9), probe="perf:large_n"),
        ],
    ),
]

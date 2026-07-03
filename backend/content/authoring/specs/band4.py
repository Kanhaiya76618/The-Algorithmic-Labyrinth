"""Levels 41-50: hard -> hardest. Advanced graphs, DP, bitmask, strings, math.

10-12 tests per question, exactly 3 visible. Adversarial edge cases required.
"""

import random

from model import Q, T
from specs.helpers import arr_case, edge_list, gen_arr, rand_ints


def _graph_case(n: int, edges: list[str], header_extra: str = "") -> str:
    head = f"{n} {len(edges)}{(' ' + header_extra) if header_extra else ''}\n"
    return head + "\n".join(edges) + ("\n" if edges else "")


QUESTIONS = [
    # ---------------- L41 (hard, graphs) ----------------
    Q(
        qid="L41-A",
        level=41,
        topic="graphs",
        title="Kingdoms Within Kingdoms",
        time_limit_s=6,
        prompt="""
Fealty in the old empire is one-way. A true kingdom is a maximal set of courts
that can all reach one another through chains of fealty. Count the kingdoms
(strongly connected components).

Input: line 1: n m (1 <= n <= 2*10^4, 0 <= m <= 10^5). Then m lines "u v"
(directed; self-loops and repeats allowed).
Output: the number of strongly connected components.
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
adj = [[] for _ in range(n + 1)]
radj = [[] for _ in range(n + 1)]
idx = 2
for _ in range(m):
    u, v = int(data[idx]), int(data[idx + 1])
    idx += 2
    adj[u].append(v)
    radj[v].append(u)
visited = [False] * (n + 1)
order = []
for s in range(1, n + 1):
    if visited[s]:
        continue
    visited[s] = True
    stack = [(s, 0)]
    while stack:
        node, i = stack.pop()
        if i < len(adj[node]):
            stack.append((node, i + 1))
            nb = adj[node][i]
            if not visited[nb]:
                visited[nb] = True
                stack.append((nb, 0))
        else:
            order.append(node)
comp = [0] * (n + 1)
count = 0
for s in reversed(order):
    if comp[s]:
        continue
    count += 1
    comp[s] = count
    stack = [s]
    while stack:
        node = stack.pop()
        for nb in radj[node]:
            if not comp[nb]:
                comp[nb] = count
                stack.append(nb)
print(count)
""",
        tests=[
            T(stdin="5 5\n1 2\n2 3\n3 1\n3 4\n4 5\n", visible=True),
            T(stdin="3 3\n1 2\n2 3\n3 1\n", visible=True),
            T(stdin="4 3\n1 2\n2 3\n3 4\n", visible=True),
            T(stdin="3 2\n1 1\n2 2\n", probe="edge:cycle"),
            T(stdin="5 0\n", probe="edge:disconnected"),
            T(stdin="6 6\n1 2\n2 1\n3 4\n4 3\n5 6\n6 5\n", probe="edge:duplicates"),
            T(stdin="1 0\n", probe="edge:single"),
            T(stdin="4 4\n1 2\n2 3\n3 4\n4 1\n", probe="edge:max-bounds"),
            T(stdin="6 7\n1 2\n2 3\n3 1\n3 4\n4 5\n5 6\n6 4\n", probe="adversarial:worst-case"),
            T(
                gen=lambda rng: _graph_case(
                    20000,
                    [f"{i} {i + 1}" for i in range(1, 20000)] + ["20000 1"] + edge_list(rng, 20000, 50000),
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L41-B",
        level=41,
        topic="graphs",
        title="Toll Roads of the Sky",
        time_limit_s=6,
        prompt="""
Sky-barges fly fixed one-way routes with tolls. Your writ allows at most k
LAYOVERS (intermediate ports) between origin s and destination t. Pay the least
total toll.

Input: line 1: n m s t k (1 <= n <= 1000, 0 <= m <= 10^4, 0 <= k < n). Then m
lines "u v w" (1 <= w <= 10^4).
Output: the cheapest fare using at most k layovers, or -1.
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
n, m, s, t, k = (int(x) for x in data[:5])
edges = []
idx = 5
for _ in range(m):
    u, v, w = int(data[idx]), int(data[idx + 1]), int(data[idx + 2])
    idx += 3
    edges.append((u, v, w))
INF = float('inf')
dist = [INF] * (n + 1)
dist[s] = 0
for _ in range(k + 1):
    nxt = dist[:]
    for u, v, w in edges:
        if dist[u] + w < nxt[v]:
            nxt[v] = dist[u] + w
    dist = nxt
print(dist[t] if dist[t] != INF else -1)
""",
        tests=[
            T(stdin="4 5 1 4 1\n1 2 100\n1 3 500\n2 3 100\n3 4 100\n2 4 600\n", visible=True),
            T(stdin="3 3 1 3 1\n1 2 100\n2 3 100\n1 3 500\n", visible=True),
            T(stdin="3 3 1 3 0\n1 2 100\n2 3 100\n1 3 500\n", visible=True),
            T(stdin="4 2 1 4 3\n1 2 5\n3 4 5\n", probe="edge:no-solution"),
            T(stdin="2 1 1 2 0\n1 2 42\n", probe="edge:single"),
            T(stdin="5 6 1 5 1\n1 2 1\n2 3 1\n3 4 1\n4 5 1\n1 5 100\n2 5 50\n", probe="adversarial:worst-case"),
            T(stdin="4 5 1 4 3\n1 2 1\n2 3 1\n3 4 1\n1 4 10\n1 4 4\n", probe="edge:duplicates"),
            T(stdin="3 2 1 1 2\n1 2 7\n2 3 7\n", probe="edge:zero"),
            T(stdin="5 5 1 5 4\n1 2 1\n2 3 1\n3 4 1\n4 5 1\n1 5 3\n", probe="edge:max-bounds"),
            T(
                gen=lambda rng: _graph_case(
                    1000,
                    [f"{i} {i + 1} {rng.randint(1, 10000)}" for i in range(1, 1000)]
                    + [f"{rng.randint(1, 1000)} {rng.randint(1, 1000)} {rng.randint(1, 10000)}" for _ in range(9000)],
                    header_extra="1 1000 999",
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L42 (hard, dynamic-programming) ----------------
    Q(
        qid="L42-A",
        level=42,
        topic="dynamic-programming",
        title="Ascent of the Frozen Peaks",
        time_limit_s=6,
        prompt="""
From any peak you may step to an adjacent peak (N/S/E/W) only if it is STRICTLY
higher. What is the longest possible ascent, counted in peaks?

Input: line 1: r c (1 <= r, c <= 500). Then r rows of c altitudes
(0 <= a <= 10^9).
Output: the length of the longest strictly increasing path.
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
r, c = int(data[0]), int(data[1])
grid = []
idx = 2
for i in range(r):
    grid.append([int(x) for x in data[idx:idx + c]])
    idx += c
cells = sorted(((grid[i][j], i, j) for i in range(r) for j in range(c)))
dp = [[1] * c for _ in range(r)]
best = 1
for val, i, j in cells:
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ni, nj = i + di, j + dj
        if 0 <= ni < r and 0 <= nj < c and grid[ni][nj] < val:
            if dp[ni][nj] + 1 > dp[i][j]:
                dp[i][j] = dp[ni][nj] + 1
    if dp[i][j] > best:
        best = dp[i][j]
print(best)
""",
        tests=[
            T(stdin="3 3\n9 9 4\n6 6 8\n2 1 1\n", visible=True),
            T(stdin="3 3\n3 4 5\n3 2 6\n2 2 1\n", visible=True),
            T(stdin="1 1\n7\n", visible=True),
            T(stdin="2 2\n5 5\n5 5\n", probe="edge:all-equal"),
            T(stdin="1 6\n1 2 3 4 5 6\n", probe="edge:sorted"),
            T(stdin="1 6\n6 5 4 3 2 1\n", probe="edge:reverse-sorted"),
            T(stdin="2 3\n1 2 3\n6 5 4\n", probe="edge:max-bounds"),
            T(stdin="2 2\n1 2\n2 3\n", probe="edge:duplicates"),
            T(stdin="3 3\n1 2 3\n8 9 4\n7 6 5\n", probe="adversarial:worst-case"),
            T(
                gen=lambda rng: "500 500\n" + "\n".join(
                    " ".join(str(rng.randint(0, 10**9)) for _ in range(500)) for _ in range(500)
                ) + "\n",
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L42-B",
        level=42,
        topic="dynamic-programming",
        title="Dragon Egg Cascade",
        time_limit_s=6,
        prompt="""
n dragon eggs sit in a row; egg i is worth v[i]. Cracking egg i pays
v[left] * v[i] * v[right] where left/right are the nearest UNCRACKED neighbours
(a missing neighbour counts as 1). Crack all eggs in the best order.

Input: line 1: n (1 <= n <= 100). Line 2: n values (0 <= v <= 100).
Output: the maximum total payout.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
vals = [1] + list(map(int, data[1:1 + n])) + [1]
m = len(vals)
dp = [[0] * m for _ in range(m)]
for length in range(2, m):
    for lo in range(m - length):
        hi = lo + length
        best = 0
        for k in range(lo + 1, hi):
            cand = dp[lo][k] + dp[k][hi] + vals[lo] * vals[k] * vals[hi]
            if cand > best:
                best = cand
        dp[lo][hi] = best
print(dp[0][m - 1])
""",
        tests=[
            T(stdin="4\n3 1 5 8\n", visible=True),
            T(stdin="2\n1 5\n", visible=True),
            T(stdin="1\n9\n", visible=True),
            T(stdin="3\n0 0 0\n", probe="edge:zero"),
            T(stdin="4\n7 7 7 7\n", probe="edge:all-equal"),
            T(stdin="2\n100 100\n", probe="edge:duplicates"),
            T(stdin="5\n1 100 1 100 1\n", probe="adversarial:worst-case"),
            T(stdin="3\n100 100 100\n", probe="edge:max-bounds"),
            T(stdin="5\n5 4 3 2 1\n", probe="edge:reverse-sorted"),
            T(gen=lambda rng: arr_case([rng.randint(0, 100) for _ in range(100)]), probe="perf:large_n"),
        ],
    ),
    # ---------------- L43 (hard, bit-manipulation) ----------------
    Q(
        qid="L43-A",
        level=43,
        topic="bit-manipulation",
        title="Thrice-Cursed Relic",
        time_limit_s=5,
        prompt="""
Every relic in the vault was triplicated by the curse - except one, which
remains unique. Find it. (Yes, some relics carry NEGATIVE auras.)

Input: line 1: n (n = 3k+1, 1 <= n <= 10^5). Line 2: n integers, |v| <= 10^9;
every value appears exactly three times except one value appearing once.
Output: the unique value.
""",
        solution=r"""
import sys
from collections import Counter
data = sys.stdin.read().split()
n = int(data[0])
counts = Counter(map(int, data[1:1 + n]))
for value, count in counts.items():
    if count == 1:
        print(value)
        break
""",
        tests=[
            T(stdin="7\n2 2 3 2 4 4 4\n", visible=True),
            T(stdin="4\n0 1 0 0\n", visible=True),
            T(stdin="1\n99\n", visible=True),
            T(stdin="4\n-5 -5 -5 -9\n", probe="edge:negative"),
            T(stdin="4\n7 0 7 7\n", probe="edge:zero"),
            T(stdin="4\n1000000000 -1000000000 1000000000 1000000000\n", probe="edge:overflow"),
            T(stdin="7\n-1 -1 -1 -2 -2 -2 -3\n", probe="edge:duplicates"),
            T(stdin="4\n999999999 999999999 999999999 1000000000\n", probe="edge:max-bounds"),
            T(stdin="10\n8 8 8 5 5 5 6 6 6 -7\n", probe="adversarial:worst-case"),
            T(
                gen=lambda rng: (lambda vals: arr_case(vals))(
                    (lambda uniq, triples: (lambda arr: (rng.shuffle(arr), arr)[1])(
                        [uniq] + [v for v in triples for _ in range(3)]
                    ))(10**9, rand_ints(rng, 33333, -10**9, 10**9 - 1))
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L43-B",
        level=43,
        topic="bit-manipulation",
        title="Resonance of Two Wands",
        time_limit_s=6,
        prompt="""
Two wands resonate with power equal to the XOR of their cores. Choose the pair
with maximum resonance.

Input: line 1: n (2 <= n <= 10^5). Line 2: n core values (0 <= v < 2^31).
Output: the maximum XOR over all pairs. (Pairwise checking is 5*10^9
operations; the trial expects better.)
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
vals = list(map(int, data[1:1 + n]))
answer = 0
mask = 0
for bit in range(30, -1, -1):
    mask |= 1 << bit
    prefixes = {v & mask for v in vals}
    candidate = answer | (1 << bit)
    if any((candidate ^ p) in prefixes for p in prefixes):
        answer = candidate
print(answer)
""",
        tests=[
            T(stdin="6\n3 10 5 25 2 8\n", visible=True),
            T(stdin="2\n1 2\n", visible=True),
            T(stdin="4\n8 1 2 12\n", visible=True),
            T(stdin="3\n7 7 7\n", probe="edge:all-equal"),
            T(stdin="2\n0 0\n", probe="edge:zero"),
            T(stdin="2\n2147483647 0\n", probe="edge:max-bounds"),
            T(stdin="4\n1 2 4 8\n", probe="adversarial:worst-case"),
            T(stdin="5\n1073741824 536870912 268435456 134217728 1\n", probe="edge:overflow"),
            T(stdin="4\n5 5 9 9\n", probe="edge:duplicates"),
            T(gen=gen_arr(100000, 0, 2**31 - 1), probe="perf:large_n"),
        ],
    ),
    # ---------------- L44 (hard, graphs + dp) ----------------
    Q(
        qid="L44-A",
        level=44,
        topic="graphs",
        title="Every Road to the Throne",
        time_limit_s=6,
        prompt="""
The succession laws form a DAG of precedence. Count the distinct chains of
succession from claimant s to the throne t, modulo 1000000007.

Input: line 1: n m s t (1 <= n <= 10^5, 0 <= m <= 2*10^5). Then m lines "u v"
(directed, acyclic guaranteed).
Output: the number of paths s -> t mod 1000000007.
""",
        solution=r"""
import sys
from collections import deque
MOD = 1000000007
data = sys.stdin.buffer.read().split()
n, m, s, t = (int(x) for x in data[:4])
adj = [[] for _ in range(n + 1)]
indeg = [0] * (n + 1)
idx = 4
for _ in range(m):
    u, v = int(data[idx]), int(data[idx + 1])
    idx += 2
    adj[u].append(v)
    indeg[v] += 1
ways = [0] * (n + 1)
ways[s] = 1
queue = deque(i for i in range(1, n + 1) if indeg[i] == 0)
while queue:
    cur = queue.popleft()
    for nb in adj[cur]:
        ways[nb] = (ways[nb] + ways[cur]) % MOD
        indeg[nb] -= 1
        if indeg[nb] == 0:
            queue.append(nb)
print(ways[t] % MOD)
""",
        tests=[
            T(stdin="4 5 1 4\n1 2\n1 3\n2 4\n3 4\n2 3\n", visible=True),
            T(stdin="3 2 1 3\n1 2\n2 3\n", visible=True),
            T(stdin="2 0 1 2\n", visible=True),
            T(stdin="4 2 1 4\n2 3\n3 4\n", probe="edge:no-solution"),
            T(stdin="1 0 1 1\n", probe="edge:single"),
            T(stdin="3 4 1 3\n1 2\n1 2\n2 3\n2 3\n", probe="edge:duplicates"),
            T(stdin="6 4 1 3\n1 2\n2 3\n4 5\n5 6\n", probe="edge:disconnected"),
            T(
                stdin="8 12 1 8\n1 2\n1 3\n2 4\n3 4\n4 5\n4 6\n5 7\n6 7\n7 8\n1 4\n4 7\n2 3\n",
                probe="adversarial:worst-case",
            ),
            T(
                gen=lambda rng: _graph_case(
                    91,
                    [f"{i} {i + 1}" for i in range(1, 91)] + [f"{i} {i + 2}" for i in range(1, 90)],
                    header_extra="1 91",
                ),
                probe="edge:overflow",
            ),
            T(
                gen=lambda rng: _graph_case(
                    100000,
                    [f"{i} {i + 1}" for i in range(1, 100000)] + [f"{i} {i + 2}" for i in range(1, 99999)],
                    header_extra="1 100000",
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L44-B",
        level=44,
        topic="graphs",
        title="March Through the Mire",
        time_limit_s=6,
        prompt="""
Every tile of the mire exacts a toll to ENTER (the starting tile's toll is paid
too). March from the north-west tile to the south-east tile moving north, south,
east or west - backtracking is allowed if it is cheaper.

Input: line 1: r c (1 <= r, c <= 500). Then r rows of c tolls (0 <= v <= 10^6).
Output: the minimum total toll. (Down-and-right-only dynamic programming will
drown here.)
""",
        solution=r"""
import sys
import heapq
data = sys.stdin.buffer.read().split()
r, c = int(data[0]), int(data[1])
grid = []
idx = 2
for i in range(r):
    grid.append([int(x) for x in data[idx:idx + c]])
    idx += c
INF = float('inf')
dist = [[INF] * c for _ in range(r)]
dist[0][0] = grid[0][0]
heap = [(grid[0][0], 0, 0)]
while heap:
    d, i, j = heapq.heappop(heap)
    if d > dist[i][j]:
        continue
    if (i, j) == (r - 1, c - 1):
        break
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ni, nj = i + di, j + dj
        if 0 <= ni < r and 0 <= nj < c:
            nd = d + grid[ni][nj]
            if nd < dist[ni][nj]:
                dist[ni][nj] = nd
                heapq.heappush(heap, (nd, ni, nj))
print(dist[r - 1][c - 1])
""",
        tests=[
            T(stdin="3 3\n1 3 1\n1 5 1\n4 2 1\n", visible=True),
            T(stdin="2 2\n1 2\n3 4\n", visible=True),
            T(stdin="1 1\n5\n", visible=True),
            T(stdin="2 2\n0 0\n0 0\n", probe="edge:zero"),
            T(stdin="3 3\n1 1 1\n1 1 1\n1 1 1\n", probe="edge:all-equal"),
            T(
                stdin="3 4\n1 1 1 1\n9 9 9 1\n1 1 1 1\n",
                probe="edge:unbalanced",
            ),
            T(
                stdin="4 4\n1 9 1 1\n1 9 1 9\n1 9 1 9\n1 1 1 9\n",
                probe="adversarial:worst-case",
            ),
            T(stdin="1 5\n3 1 4 1 5\n", probe="edge:single"),
            T(stdin="2 3\n1000000 1000000 1000000\n1000000 1000000 1000000\n", probe="edge:max-bounds"),
            T(
                gen=lambda rng: "500 500\n" + "\n".join(
                    " ".join(str(rng.randint(0, 10**6)) for _ in range(500)) for _ in range(500)
                ) + "\n",
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L45 BOSS x3 (very hard) ----------------
    Q(
        qid="L45-B1",
        level=45,
        topic="two-pointers",
        title="Deluge in the Undercroft",
        is_boss=True,
        time_limit_s=6,
        prompt="""
BOSS. The undercroft's pillars have varying heights; the deluge fills every
hollow between them. How much water stands when the rain stops?

Input: line 1: n (1 <= n <= 2*10^5). Line 2: n pillar heights (0 <= h <= 10^9).
Output: the total volume of trapped water.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
h = list(map(int, data[1:1 + n]))
lo, hi = 0, n - 1
lmax, rmax = 0, 0
water = 0
while lo < hi:
    if h[lo] <= h[hi]:
        lmax = max(lmax, h[lo])
        water += lmax - h[lo]
        lo += 1
    else:
        rmax = max(rmax, h[hi])
        water += rmax - h[hi]
        hi -= 1
print(water)
""",
        tests=[
            T(stdin="12\n0 1 0 2 1 0 1 3 2 1 2 1\n", visible=True),
            T(stdin="6\n4 2 0 3 2 5\n", visible=True),
            T(stdin="3\n3 0 3\n", visible=True),
            T(stdin="5\n1 2 3 4 5\n", probe="edge:sorted"),
            T(stdin="4\n7 7 7 7\n", probe="edge:all-equal"),
            T(stdin="2\n9 4\n", probe="edge:single"),
            T(stdin="5\n0 0 0 0 0\n", probe="edge:zero"),
            T(stdin="5\n1000000000 0 1000000000 0 1000000000\n", probe="edge:max-bounds"),
            T(stdin="7\n5 1 4 1 3 1 5\n", probe="adversarial:worst-case"),
            T(stdin="6\n2 1 0 0 1 2\n", probe="edge:unbalanced"),
            T(gen=gen_arr(200000, 0, 10**9), probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L45-B2",
        level=45,
        topic="dynamic-programming",
        title="Tongue of the Ancients",
        is_boss=True,
        time_limit_s=6,
        prompt="""
BOSS. An unbroken inscription must be parsed into words of the ancient lexicon
(words may repeat). Can it be done?

Input: line 1: d (1 <= d <= 1000) - lexicon size. Line 2: the inscription
(1..10^4 lowercase letters). Then d lexicon words (1..20 letters each).
Output: YES if the inscription segments completely, else NO.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
d = int(data[0])
s = data[1]
words = set(data[2:2 + d])
maxlen = max(len(w) for w in words)
n = len(s)
dp = [False] * (n + 1)
dp[0] = True
for i in range(1, n + 1):
    for L in range(1, min(maxlen, i) + 1):
        if dp[i - L] and s[i - L:i] in words:
            dp[i] = True
            break
print("YES" if dp[n] else "NO")
""",
        tests=[
            T(stdin="2\nleetcode\nleet code\n", visible=True),
            T(stdin="2\napplepenapple\napple pen\n", visible=True),
            T(stdin="3\ncatsandog\ncats dog sand\n", visible=True),
            T(stdin="1\naaaaaa\na\n", probe="edge:single"),
            T(stdin="2\nabab\nab abab\n", probe="edge:duplicates"),
            T(stdin="1\nzzzzy\nz\n", probe="edge:no-solution"),
            T(stdin="1\ndungeonofrecall\ndungeonofrecall\n", probe="edge:max-bounds"),
            T(
                gen=lambda rng: "3\n" + "a" * 9999 + "b\n" + "a aa aaa\n",
                probe="adversarial:worst-case",
            ),
            T(
                gen=lambda rng: "3\n" + "a" * 10000 + "\na aa aaa\n",
                probe="perf:large_n",
            ),
            T(stdin="2\nab\nabc a\n", probe="edge:unbalanced"),
        ],
    ),
    Q(
        qid="L45-B3",
        level=45,
        topic="binary-search",
        title="Lattice of Sorted Fates",
        is_boss=True,
        time_limit_s=6,
        prompt="""
BOSS. The lattice of fates is an n x n grid sorted along every row and every
column. Name the k-th smallest fate.

Input: line 1: n k (1 <= n <= 1000, 1 <= k <= n^2). Then n rows of n integers
(|v| <= 10^9), each row and column non-decreasing.
Output: the k-th smallest value in the whole lattice.
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
n, k = int(data[0]), int(data[1])
grid = []
idx = 2
for i in range(n):
    grid.append([int(x) for x in data[idx:idx + n]])
    idx += n

def count_le(x):
    count = 0
    j = n - 1
    for row in grid:
        while j >= 0 and row[j] > x:
            j -= 1
        count += j + 1
    return count

lo, hi = grid[0][0], grid[n - 1][n - 1]
while lo < hi:
    mid = (lo + hi) // 2
    if count_le(mid) >= k:
        hi = mid
    else:
        lo = mid + 1
print(lo)
""",
        tests=[
            T(stdin="3 8\n1 5 9\n10 11 13\n12 13 15\n", visible=True),
            T(stdin="2 2\n1 2\n1 3\n", visible=True),
            T(stdin="2 1\n-5 0\n-3 4\n", visible=True),
            T(stdin="2 4\n1 2\n3 4\n", probe="edge:max-bounds"),
            T(stdin="1 1\n7\n", probe="edge:single"),
            T(stdin="3 5\n2 2 2\n2 2 2\n2 2 2\n", probe="edge:all-equal"),
            T(stdin="3 4\n1 1 3\n1 1 3\n3 3 3\n", probe="edge:duplicates"),
            T(stdin="2 3\n-9 -7\n-8 -1\n", probe="edge:negative"),
            T(
                stdin="3 7\n1 2 100\n3 4 101\n5 6 102\n",
                probe="edge:unbalanced",
            ),
            T(stdin="3 9\n1 2 3\n4 5 6\n7 8 1000000000\n", probe="adversarial:worst-case"),
            T(
                gen=lambda rng: (lambda rows: f"1000 500000\n" + "\n".join(" ".join(map(str, row)) for row in rows) + "\n")(
                    [[i * 1000 + j for j in range(1000)] for i in range(1000)]
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L46 (hard, math) ----------------
    Q(
        qid="L46-A",
        level=46,
        topic="math",
        title="Countless Banners",
        time_limit_s=6,
        prompt="""
From n banners choose r to fly over the gate. Count the ways, modulo
1000000007.

Input: one line: n r (0 <= n <= 10^6, 0 <= r <= 10^6).
Output: C(n, r) mod 1000000007 (0 when r > n). Factorials this size demand
modular inverses.
""",
        solution=r"""
import sys
MOD = 1000000007
n, r = map(int, sys.stdin.read().split())
if r > n:
    print(0)
else:
    num = 1
    for i in range(n, n - r, -1):
        num = num * (i % MOD) % MOD
    den = 1
    for i in range(1, r + 1):
        den = den * i % MOD
    print(num * pow(den, MOD - 2, MOD) % MOD)
""",
        tests=[
            T(stdin="5 2\n", visible=True),
            T(stdin="10 3\n", visible=True),
            T(stdin="52 5\n", visible=True),
            T(stdin="7 0\n", probe="edge:zero"),
            T(stdin="9 9\n", probe="edge:max-bounds"),
            T(stdin="3 5\n", probe="edge:no-solution"),
            T(stdin="1 1\n", probe="edge:single"),
            T(stdin="67 33\n", probe="edge:overflow"),
            T(stdin="100 50\n", probe="adversarial:worst-case"),
            T(stdin="1000000 500000\n", probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L46-B",
        level=46,
        topic="math",
        title="Prophecy of the Golden Spiral",
        time_limit_s=5,
        prompt="""
The prophecy names the n-th number of the golden spiral: F(0)=0, F(1)=1,
F(n)=F(n-1)+F(n-2). Speak it modulo 1000000007.

Input: one integer n (0 <= n <= 10^18).
Output: F(n) mod 1000000007. (A trillion-trillion loop iterations will not
finish before the prophecy expires; double fast or exponentiate matrices.)
""",
        solution=r"""
import sys
MOD = 1000000007

def fib(n):
    if n == 0:
        return (0, 1)
    a, b = fib(n >> 1)
    c = a * ((2 * b - a) % MOD) % MOD
    d = (a * a + b * b) % MOD
    if n & 1:
        return (d, (c + d) % MOD)
    return (c, d)

n = int(sys.stdin.read())
print(fib(n)[0] % MOD)
""",
        tests=[
            T(stdin="10\n", visible=True),
            T(stdin="1\n", visible=True),
            T(stdin="20\n", visible=True),
            T(stdin="0\n", probe="edge:zero"),
            T(stdin="2\n", probe="edge:single"),
            T(stdin="93\n", probe="edge:overflow"),
            T(stdin="1000000000000000000\n", probe="edge:max-bounds"),
            T(stdin="999999999999999989\n", probe="perf:large_n"),
            T(stdin="576460752303423488\n", probe="adversarial:worst-case"),
            T(stdin="1000000\n", probe="edge:duplicates"),
        ],
    ),
    # ---------------- L47 (hard, strings) ----------------
    Q(
        qid="L47-A",
        level=47,
        topic="strings",
        title="Echoes in the Long Hall",
        time_limit_s=6,
        prompt="""
How many times does the war-cry echo inside the long hall's inscription?
Overlapping echoes count separately.

Input: line 1: the inscription (1..2*10^5 lowercase letters). Line 2: the
war-cry (1..10^5 lowercase letters).
Output: the number of (possibly overlapping) occurrences. (Naive scanning of
periodic text will echo forever; the Knuth-Morris-Pratt rite is expected.)
""",
        solution=r"""
import sys
text, pattern = sys.stdin.read().split()
m = len(pattern)
if m > len(text):
    print(0)
else:
    fail = [0] * m
    k = 0
    for i in range(1, m):
        while k and pattern[i] != pattern[k]:
            k = fail[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        fail[i] = k
    count = 0
    k = 0
    for c in text:
        while k and c != pattern[k]:
            k = fail[k - 1]
        if c == pattern[k]:
            k += 1
        if k == m:
            count += 1
            k = fail[k - 1]
    print(count)
""",
        tests=[
            T(stdin="abababa\naba\n", visible=True),
            T(stdin="aaaaa\naa\n", visible=True),
            T(stdin="dungeon\nrecall\n", visible=True),
            T(stdin="ab\nabc\n", probe="edge:no-solution"),
            T(stdin="torch\ntorch\n", probe="edge:max-bounds"),
            T(stdin="zzzzzz\nz\n", probe="edge:single"),
            T(stdin="aaaa\naaa\n", probe="edge:duplicates"),
            T(stdin="bbbbbb\nbb\n", probe="edge:all-equal"),
            T(gen=lambda rng: "ab" * 100000 + "\n" + "ab" * 50000 + "\n", probe="adversarial:worst-case"),
            T(gen=lambda rng: "a" * 200000 + "\n" + "a" * 100000 + "\n", probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L47-B",
        level=47,
        topic="strings",
        title="Seal of Self-Similarity",
        time_limit_s=5,
        prompt="""
The seal's strength is the length of the longest PROPER prefix of the
inscription that is also its suffix.

Input: one line of 1..2*10^5 lowercase letters.
Output: that length (0 if no proper prefix matches a suffix).
""",
        solution=r"""
import sys
s = sys.stdin.read().strip()
n = len(s)
fail = [0] * n
k = 0
for i in range(1, n):
    while k and s[i] != s[k]:
        k = fail[k - 1]
    if s[i] == s[k]:
        k += 1
    fail[i] = k
print(fail[n - 1] if n > 0 else 0)
""",
        tests=[
            T(stdin="ababcab\n", visible=True),
            T(stdin="aaaa\n", visible=True),
            T(stdin="abcdef\n", visible=True),
            T(stdin="x\n", probe="edge:single"),
            T(stdin="zz\n", probe="edge:all-equal"),
            T(stdin="abcab\n", probe="edge:duplicates"),
            T(stdin="ababab\n", probe="edge:max-bounds"),
            T(stdin="aabaa\n", probe="adversarial:worst-case"),
            T(stdin="ba\n", probe="edge:no-solution"),
            T(gen=lambda rng: "ab" * 100000 + "\n", probe="perf:large_n"),
        ],
    ),
    # ---------------- L48 (hard, graphs) ----------------
    Q(
        qid="L48-A",
        level=48,
        topic="graphs",
        title="Bridges of the Chasm",
        time_limit_s=6,
        prompt="""
Some rope bridges are the ONLY link between parts of the undercity: cut one and
the city splits. Count these critical bridges.

Input: line 1: n m (1 <= n <= 5*10^4, 0 <= m <= 10^5). Then m lines "u v"
(undirected; parallel bridges and self-loops possible - a parallel pair is
never critical).
Output: the number of bridges.
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
adj = [[] for _ in range(n + 1)]
idx = 2
for e in range(m):
    u, v = int(data[idx]), int(data[idx + 1])
    idx += 2
    adj[u].append((v, e))
    adj[v].append((u, e))
disc = [0] * (n + 1)
low = [0] * (n + 1)
timer = 1
bridges = 0
for s in range(1, n + 1):
    if disc[s]:
        continue
    disc[s] = low[s] = timer
    timer += 1
    stack = [(s, -1, iter(adj[s]))]
    while stack:
        node, pedge, it = stack[-1]
        advanced = False
        for nb, eid in it:
            if eid == pedge:
                continue
            if disc[nb]:
                if disc[nb] < low[node]:
                    low[node] = disc[nb]
            else:
                disc[nb] = low[nb] = timer
                timer += 1
                stack.append((nb, eid, iter(adj[nb])))
                advanced = True
                break
        if not advanced:
            stack.pop()
            if stack:
                parent = stack[-1][0]
                if low[node] < low[parent]:
                    low[parent] = low[node]
                if low[node] > disc[parent]:
                    bridges += 1
print(bridges)
""",
        tests=[
            T(stdin="5 5\n1 2\n2 3\n3 1\n3 4\n4 5\n", visible=True),
            T(stdin="4 4\n1 2\n2 3\n3 4\n4 1\n", visible=True),
            T(stdin="4 3\n1 2\n2 3\n3 4\n", visible=True),
            T(stdin="3 3\n1 2\n1 2\n2 3\n", probe="edge:duplicates"),
            T(stdin="4 4\n1 2\n2 3\n3 1\n4 4\n", probe="edge:cycle"),
            T(stdin="6 4\n1 2\n2 3\n4 5\n5 6\n", probe="edge:disconnected"),
            T(stdin="2 1\n1 2\n", probe="edge:single"),
            T(stdin="7 7\n1 2\n2 3\n3 1\n3 4\n4 5\n5 6\n6 4\n", probe="adversarial:worst-case"),
            T(stdin="5 4\n1 2\n2 3\n3 4\n4 5\n", probe="edge:max-bounds"),
            T(
                gen=lambda rng: _graph_case(
                    50000,
                    [f"{i} {i + 1}" for i in range(1, 50000)]
                    + [f"{rng.randint(1, 25000)} {rng.randint(25001, 50000)}" for _ in range(50000)],
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L48-B",
        level=48,
        topic="graphs",
        title="Pillars That Hold the Sky",
        time_limit_s=6,
        prompt="""
Some pillars are load-bearing: remove one and its wing of the undercity falls
away from the rest. Count the load-bearing pillars (articulation points).

Input: line 1: n m (1 <= n <= 5*10^4, 0 <= m <= 10^5). Then m lines "u v"
(undirected).
Output: the number of articulation points.
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
adj = [[] for _ in range(n + 1)]
idx = 2
for e in range(m):
    u, v = int(data[idx]), int(data[idx + 1])
    idx += 2
    if u != v:
        adj[u].append((v, e))
        adj[v].append((u, e))
disc = [0] * (n + 1)
low = [0] * (n + 1)
is_ap = [False] * (n + 1)
timer = 1
for s in range(1, n + 1):
    if disc[s]:
        continue
    disc[s] = low[s] = timer
    timer += 1
    root_children = 0
    stack = [(s, -1, iter(adj[s]))]
    while stack:
        node, pedge, it = stack[-1]
        advanced = False
        for nb, eid in it:
            if eid == pedge:
                continue
            if disc[nb]:
                if disc[nb] < low[node]:
                    low[node] = disc[nb]
            else:
                disc[nb] = low[nb] = timer
                timer += 1
                if node == s:
                    root_children += 1
                stack.append((nb, eid, iter(adj[nb])))
                advanced = True
                break
        if not advanced:
            stack.pop()
            if stack:
                parent = stack[-1][0]
                if low[node] < low[parent]:
                    low[parent] = low[node]
                if parent != s and low[node] >= disc[parent]:
                    is_ap[parent] = True
    if root_children >= 2:
        is_ap[s] = True
print(sum(is_ap))
""",
        tests=[
            T(stdin="5 5\n1 2\n2 3\n3 1\n3 4\n4 5\n", visible=True),
            T(stdin="4 4\n1 2\n2 3\n3 4\n4 1\n", visible=True),
            T(stdin="4 3\n1 2\n1 3\n1 4\n", visible=True),
            T(stdin="5 4\n1 2\n2 3\n3 4\n4 5\n", probe="edge:max-bounds"),
            T(stdin="3 3\n1 2\n2 3\n3 1\n", probe="edge:cycle"),
            T(stdin="6 4\n1 2\n2 3\n4 5\n5 6\n", probe="edge:disconnected"),
            T(stdin="2 1\n1 2\n", probe="edge:single"),
            T(stdin="7 8\n1 2\n2 3\n3 1\n3 4\n4 5\n5 6\n6 4\n3 7\n", probe="adversarial:worst-case"),
            T(stdin="4 5\n1 2\n1 2\n2 3\n3 4\n2 4\n", probe="edge:duplicates"),
            T(
                gen=lambda rng: _graph_case(50000, [f"{i} {i + 1}" for i in range(1, 50000)]),
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L49 (hard, bitmask dp) ----------------
    Q(
        qid="L49-A",
        level=49,
        topic="dynamic-programming",
        title="Circuit of the Wandering Flame",
        time_limit_s=6,
        prompt="""
The flame must visit all n shrines exactly once, starting and ending at shrine
1, paying each passage's toll. Find the cheapest full circuit.

Input: line 1: n (2 <= n <= 12). Then n rows of n tolls; row i column j is the
toll from shrine i to shrine j (0 on the diagonal, tolls may be asymmetric,
0 <= toll <= 10^6).
Output: the minimum circuit cost.
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
n = int(data[0])
cost = []
idx = 1
for i in range(n):
    cost.append([int(x) for x in data[idx:idx + n]])
    idx += n
FULL = 1 << n
INF = float('inf')
dp = [[INF] * n for _ in range(FULL)]
dp[1][0] = 0
for mask in range(1, FULL):
    if not mask & 1:
        continue
    row = dp[mask]
    for last in range(n):
        cur = row[last]
        if cur == INF or not mask >> last & 1:
            continue
        for nxt in range(n):
            if mask >> nxt & 1:
                continue
            nmask = mask | (1 << nxt)
            cand = cur + cost[last][nxt]
            if cand < dp[nmask][nxt]:
                dp[nmask][nxt] = cand
print(min(dp[FULL - 1][last] + cost[last][0] for last in range(1, n)) if n > 1 else 0)
""",
        tests=[
            T(stdin="4\n0 10 15 20\n10 0 35 25\n15 35 0 30\n20 25 30 0\n", visible=True),
            T(stdin="3\n0 1 10\n1 0 1\n10 1 0\n", visible=True),
            T(stdin="2\n0 7\n3 0\n", visible=True),
            T(stdin="3\n0 5 5\n5 0 5\n5 5 0\n", probe="edge:all-equal"),
            T(stdin="3\n0 0 9\n9 0 0\n0 9 0\n", probe="edge:zero"),
            T(stdin="4\n0 1 100 100\n100 0 1 100\n100 100 0 1\n1 100 100 0\n", probe="adversarial:worst-case"),
            T(stdin="3\n0 1000000 1000000\n1000000 0 1000000\n1000000 1000000 0\n", probe="edge:max-bounds"),
            T(stdin="4\n0 1 2 3\n9 0 1 2\n9 9 0 1\n1 9 9 0\n", probe="edge:unbalanced"),
            T(stdin="2\n0 1000000\n1000000 0\n", probe="edge:single"),
            T(
                gen=lambda rng: "12\n" + "\n".join(
                    " ".join("0" if i == j else str(rng.randint(1, 10**6)) for j in range(12)) for i in range(12)
                ) + "\n",
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L49-B",
        level=49,
        topic="dynamic-programming",
        title="Every Path of the Pilgrim",
        time_limit_s=6,
        prompt="""
The pilgrim must walk every shrine exactly once along existing trails. Count
the distinct pilgrimages; a route and its exact reverse are the SAME
pilgrimage. A lone shrine counts as one pilgrimage.

Input: line 1: n m (1 <= n <= 10, 0 <= m <= 45). Then m lines "u v"
(undirected, no self-loops, no repeats).
Output: the number of Hamiltonian paths.
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
adj = [0] * n
idx = 2
for _ in range(m):
    u, v = int(data[idx]) - 1, int(data[idx + 1]) - 1
    idx += 2
    adj[u] |= 1 << v
    adj[v] |= 1 << u
if n == 1:
    print(1)
else:
    FULL = 1 << n
    dp = [[0] * n for _ in range(FULL)]
    for i in range(n):
        dp[1 << i][i] = 1
    for mask in range(1, FULL):
        for last in range(n):
            ways = dp[mask][last]
            if not ways or not mask >> last & 1:
                continue
            nbrs = adj[last] & ~mask
            while nbrs:
                nxt_bit = nbrs & -nbrs
                nbrs ^= nxt_bit
                nxt = nxt_bit.bit_length() - 1
                dp[mask | nxt_bit][nxt] += ways
    total = sum(dp[FULL - 1])
    print(total // 2)
""",
        tests=[
            T(stdin="3 3\n1 2\n2 3\n1 3\n", visible=True),
            T(stdin="3 2\n1 2\n2 3\n", visible=True),
            T(stdin="4 6\n1 2\n1 3\n1 4\n2 3\n2 4\n3 4\n", visible=True),
            T(stdin="1 0\n", probe="edge:single"),
            T(stdin="4 0\n", probe="edge:no-solution"),
            T(stdin="5 4\n1 2\n2 3\n4 5\n3 4\n", probe="adversarial:worst-case"),
            T(stdin="6 5\n1 2\n2 3\n3 4\n4 5\n1 6\n", probe="edge:unbalanced"),
            T(stdin="5 4\n1 2\n2 3\n3 4\n1 5\n", probe="edge:disconnected"),
            T(stdin="4 4\n1 2\n2 3\n3 4\n4 1\n", probe="edge:cycle"),
            T(
                gen=lambda rng: "10 45\n" + "\n".join(f"{u} {v}" for u in range(1, 11) for v in range(u + 1, 11)) + "\n",
                probe="edge:max-bounds",
            ),
            T(
                gen=lambda rng: "10 45\n" + "\n".join(f"{u} {v}" for u in range(1, 11) for v in range(u + 1, 11)) + "\n",
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L50 FINAL BOSS x3 (hardest) ----------------
    Q(
        qid="L50-B1",
        level=50,
        topic="heaps",
        title="The Middle Voice of the Choir",
        is_boss=True,
        time_limit_s=8,
        prompt="""
FINAL BOSS. Choristers join one by one. After EACH arrival, the conductor calls
out the middle voice: the median pitch, and with an even choir the LOWER of the
two middle pitches.

Input: line 1: n (1 <= n <= 2*10^5). Line 2: n pitches, |v| <= 10^9, in arrival
order.
Output: n medians, space-separated. (Re-sorting after every arrival is a dirge
of O(n^2 log n); keep two heaps instead.)
""",
        solution=r"""
import sys
import heapq
data = sys.stdin.buffer.read().split()
n = int(data[0])
lo = []  # max-heap (negated): smaller half
hi = []  # min-heap: larger half
out = []
for tok in data[1:1 + n]:
    v = int(tok)
    if not lo or v <= -lo[0]:
        heapq.heappush(lo, -v)
    else:
        heapq.heappush(hi, v)
    if len(lo) > len(hi) + 1:
        heapq.heappush(hi, -heapq.heappop(lo))
    elif len(hi) > len(lo):
        heapq.heappush(lo, -heapq.heappop(hi))
    out.append(str(-lo[0]))
sys.stdout.write(" ".join(out) + "\n")
""",
        tests=[
            T(stdin="5\n2 1 5 7 2\n", visible=True),
            T(stdin="4\n5 15 1 3\n", visible=True),
            T(stdin="1\n42\n", visible=True),
            T(stdin="6\n1 2 3 4 5 6\n", probe="edge:sorted"),
            T(stdin="6\n6 5 4 3 2 1\n", probe="edge:reverse-sorted"),
            T(stdin="5\n7 7 7 7 7\n", probe="edge:all-equal"),
            T(stdin="4\n-1 -10 -3 -7\n", probe="edge:negative"),
            T(stdin="6\n1000000000 -1000000000 0 999999999 -999999999 1\n", probe="edge:max-bounds"),
            T(stdin="8\n100 -100 100 -100 100 -100 100 -100\n", probe="adversarial:worst-case"),
            T(stdin="3\n0 0 0\n", probe="edge:zero"),
            T(gen=gen_arr(200000, -10**9, 10**9), probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L50-B2",
        level=50,
        topic="strings",
        title="Lexicon of Infinite Whispers",
        is_boss=True,
        time_limit_s=8,
        prompt="""
FINAL BOSS. Every distinct substring of the inscription is a whisper the boss
has already catalogued. Count the catalogue's size.

Input: one line of 1..5*10^4 lowercase letters.
Output: the number of distinct non-empty substrings. (The count overflows
32-bit integers, and enumerating substrings outright will be devoured; a
suffix automaton or suffix array survives.)
""",
        solution=r"""
import sys
s = sys.stdin.read().strip()
maxn = 2 * len(s) + 5
link = [-1] * maxn
length = [0] * maxn
trans = [None] * maxn
trans[0] = {}
last = 0
size = 1
for c in s:
    cur = size
    size += 1
    length[cur] = length[last] + 1
    trans[cur] = {}
    p = last
    while p != -1 and c not in trans[p]:
        trans[p][c] = cur
        p = link[p]
    if p == -1:
        link[cur] = 0
    else:
        q = trans[p][c]
        if length[p] + 1 == length[q]:
            link[cur] = q
        else:
            clone = size
            size += 1
            length[clone] = length[p] + 1
            trans[clone] = dict(trans[q])
            link[clone] = link[q]
            while p != -1 and trans[p].get(c) == q:
                trans[p][c] = clone
                p = link[p]
            link[q] = clone
            link[cur] = clone
    last = cur
print(sum(length[v] - length[link[v]] for v in range(1, size)))
""",
        tests=[
            T(stdin="abc\n", visible=True),
            T(stdin="aaa\n", visible=True),
            T(stdin="abab\n", visible=True),
            T(stdin="z\n", probe="edge:single"),
            T(stdin="zzzzzzzzzz\n", probe="edge:all-equal"),
            T(stdin="abcdefghij\n", probe="edge:max-bounds"),
            T(stdin="ababababab\n", probe="adversarial:worst-case"),
            T(stdin="aabbaabb\n", probe="edge:duplicates"),
            T(gen=lambda rng: "".join(rng.choice("ab") for _ in range(50000)) + "\n", probe="edge:overflow"),
            T(gen=lambda rng: "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(50000)) + "\n", probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L50-B3",
        level=50,
        topic="greedy",
        title="The Final Ledger",
        is_boss=True,
        time_limit_s=8,
        prompt="""
FINAL BOSS. The Boss's ledger lists n contracts: a start day, an end day and a
bounty. You may work only one contract at a time; a contract may begin the very
day another ends. Choose contracts to maximize the total bounty.

Input: line 1: n (1 <= n <= 10^5). Then n lines "s e b"
(0 <= s < e <= 10^9, 1 <= b <= 10^9).
Output: the maximum total bounty. (Sort by end day; bisect for the last
compatible contract; the greedy of grabbing the biggest bounty first is the
Boss's favourite trap.)
""",
        solution=r"""
import sys
from bisect import bisect_right
data = sys.stdin.buffer.read().split()
n = int(data[0])
jobs = []
idx = 1
for _ in range(n):
    s, e, b = int(data[idx]), int(data[idx + 1]), int(data[idx + 2])
    idx += 3
    jobs.append((e, s, b))
jobs.sort()
ends = [j[0] for j in jobs]
dp = [0] * (n + 1)
for i, (e, s, b) in enumerate(jobs):
    j = bisect_right(ends, s, 0, i)
    take = dp[j] + b
    dp[i + 1] = take if take > dp[i] else dp[i]
print(dp[n])
""",
        tests=[
            T(stdin="4\n1 2 50\n3 5 20\n6 19 100\n2 100 200\n", visible=True),
            T(stdin="3\n1 2 5\n2 3 5\n3 4 5\n", visible=True),
            T(stdin="1\n0 1000000000 7\n", visible=True),
            T(stdin="3\n1 10 10\n2 3 1\n4 5 1\n", probe="adversarial:worst-case"),
            T(stdin="4\n1 5 10\n1 5 10\n1 5 10\n1 5 10\n", probe="edge:duplicates"),
            T(stdin="3\n1 4 3\n2 5 3\n3 6 3\n", probe="edge:all-equal"),
            T(stdin="2\n0 5 9\n5 9 9\n", probe="edge:zero"),
            T(stdin="4\n1 2 1\n3 4 1\n5 6 1\n7 8 1\n", probe="edge:sorted"),
            T(stdin="2\n1 1000000000 1000000000\n2 3 999999999\n", probe="edge:max-bounds"),
            T(stdin="3\n5 6 4\n1 9 5\n7 8 4\n", probe="edge:unbalanced"),
            T(
                gen=lambda rng: "100000\n" + "".join(
                    (lambda s: f"{s} {s + rng.randint(1, 1000)} {rng.randint(1, 10**9)}\n")(rng.randint(0, 10**9 - 1001))
                    for _ in range(100000)
                ),
                probe="perf:large_n",
            ),
        ],
    ),
]

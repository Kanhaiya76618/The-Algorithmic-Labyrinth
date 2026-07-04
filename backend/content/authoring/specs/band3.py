"""Levels 26-40: medium-hard -> hard. Graphs, DP, greedy, advanced binary search.

8-10 tests per question, 2-3 visible. Edge-case probes are mandatory here:
empty input, single element, max bounds, duplicates.
"""

import random

from model import Q, T
from specs.helpers import arr_case, edge_list, gen_arr, rand_ints


def _grid(rng: random.Random, r: int, c: int, land_chance: float) -> str:
    rows = ["".join("#" if rng.random() < land_chance else "." for _ in range(c)) for _ in range(r)]
    return f"{r} {c}\n" + "\n".join(rows) + "\n"


def _graph_case(n: int, edges: list[str], extra: str = "") -> str:
    head = f"{n} {len(edges)}\n"
    body = "\n".join(edges) + ("\n" if edges else "")
    return head + body + (extra if not extra or extra.endswith("\n") else extra + "\n")


QUESTIONS = [
    # ---------------- L26 (medium-hard, graphs) ----------------
    Q(
        qid="L26-A",
        level=26,
        topic="graphs",
        title="Shattered Realms",
        time_limit_s=5,
        prompt="""
The old kingdom's n keeps were once linked by m bridges (bidirectional). Count
how many isolated realms remain.

Input: line 1: n m (1 <= n <= 10^5, 0 <= m <= 2*10^5). Then m lines "u v"
(1-based; self-loops and repeated bridges may appear).
Output: the number of connected components.
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
parent = list(range(n + 1))

def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

idx = 2
for _ in range(m):
    u, v = int(data[idx]), int(data[idx + 1])
    idx += 2
    ru, rv = find(u), find(v)
    if ru != rv:
        parent[ru] = rv
print(len({find(i) for i in range(1, n + 1)}))
""",
        tests=[
            T(stdin="5 3\n1 2\n2 3\n4 5\n", visible=True),
            T(stdin="4 4\n1 2\n2 3\n3 4\n4 1\n", visible=True),
            T(stdin="6 0\n", probe="edge:disconnected"),
            T(stdin="4 6\n1 2\n1 2\n2 3\n3 4\n4 1\n2 4\n", probe="edge:duplicates"),
            T(stdin="3 2\n1 1\n2 2\n", probe="edge:cycle"),
            T(stdin="1 0\n", probe="edge:single"),
            T(stdin="5 4\n1 2\n2 3\n3 4\n4 5\n", probe="edge:max-bounds"),
            T(
                gen=lambda rng: _graph_case(100000, edge_list(rng, 100000, 150000)),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L26-B",
        level=26,
        topic="graphs",
        title="Beacon Relay",
        time_limit_s=5,
        prompt="""
A warning must travel from beacon s to beacon t across bidirectional sightlines,
one hop per night. How many nights does the fastest relay take?

Input: line 1: n m s t (1 <= n <= 10^5, 0 <= m <= 2*10^5). Then m lines "u v".
Output: the minimum number of hops, or -1 if the warning can never arrive.
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.buffer.read().split()
n, m, s, t = (int(x) for x in data[:4])
adj = [[] for _ in range(n + 1)]
idx = 4
for _ in range(m):
    u, v = int(data[idx]), int(data[idx + 1])
    idx += 2
    adj[u].append(v)
    adj[v].append(u)
dist = [-1] * (n + 1)
dist[s] = 0
queue = deque([s])
while queue:
    cur = queue.popleft()
    if cur == t:
        break
    for nb in adj[cur]:
        if dist[nb] == -1:
            dist[nb] = dist[cur] + 1
            queue.append(nb)
print(dist[t])
""",
        tests=[
            T(stdin="5 5 1 5\n1 2\n2 3\n3 5\n1 4\n4 5\n", visible=True),
            T(stdin="4 2 1 4\n1 2\n3 4\n", visible=True),
            T(stdin="3 1 2 2\n1 3\n", probe="edge:zero"),
            T(stdin="6 3 1 6\n1 2\n2 3\n4 5\n", probe="edge:no-solution"),
            T(stdin="5 6 1 4\n1 2\n2 3\n3 1\n3 4\n4 5\n5 3\n", probe="edge:cycle"),
            T(stdin="2 1 1 2\n1 2\n", probe="edge:single"),
            T(stdin="7 8 1 7\n1 2\n1 3\n2 4\n3 4\n4 5\n4 6\n5 7\n6 7\n", probe="adversarial:worst-case"),
            T(
                gen=lambda rng: _graph_case(
                    100000,
                    [f"{i} {i + 1}" for i in range(1, 100000)] + edge_list(rng, 100000, 50000),
                ).replace("\n", " 1 100000\n", 1),
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L27 (medium-hard, graphs) ----------------
    Q(
        qid="L27-A",
        level=27,
        topic="graphs",
        title="Ouroboros Court",
        time_limit_s=5,
        prompt="""
Every noble of the court owes fealty to others (directed). The realm collapses
if any chain of fealty loops back on itself. Does it?

Input: line 1: n m (1 <= n <= 10^5, 0 <= m <= 2*10^5). Then m lines "u v"
meaning u owes fealty to v.
Output: YES if the directed graph contains a cycle, else NO.
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
adj = [[] for _ in range(n + 1)]
indeg = [0] * (n + 1)
idx = 2
for _ in range(m):
    u, v = int(data[idx]), int(data[idx + 1])
    idx += 2
    adj[u].append(v)
    indeg[v] += 1
queue = deque(i for i in range(1, n + 1) if indeg[i] == 0)
seen = 0
while queue:
    cur = queue.popleft()
    seen += 1
    for nb in adj[cur]:
        indeg[nb] -= 1
        if indeg[nb] == 0:
            queue.append(nb)
print("NO" if seen == n else "YES")
""",
        tests=[
            T(stdin="3 3\n1 2\n2 3\n3 1\n", visible=True),
            T(stdin="4 3\n1 2\n1 3\n2 4\n", visible=True),
            T(stdin="2 1\n1 1\n", probe="edge:cycle"),
            T(stdin="4 4\n1 2\n1 3\n2 4\n3 4\n", probe="adversarial:worst-case"),
            T(stdin="6 4\n1 2\n2 1\n4 5\n5 6\n", probe="edge:disconnected"),
            T(stdin="5 4\n1 2\n2 3\n3 4\n4 5\n", probe="edge:no-solution"),
            T(stdin="1 0\n", probe="edge:single"),
            T(
                gen=lambda rng: _graph_case(100000, [f"{i} {i + 1}" for i in range(1, 100000)]),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L27-B",
        level=27,
        topic="graphs",
        title="Two Banners",
        time_limit_s=5,
        prompt="""
Every pair of feuding houses must march under different banners, and only two
banners exist. Feuds are bidirectional. Can the houses be split?

Input: line 1: n m (1 <= n <= 10^5, 0 <= m <= 2*10^5). Then m lines "u v".
Output: YES if the graph is bipartite, else NO.
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
adj = [[] for _ in range(n + 1)]
idx = 2
for _ in range(m):
    u, v = int(data[idx]), int(data[idx + 1])
    idx += 2
    adj[u].append(v)
    adj[v].append(u)
color = [0] * (n + 1)
ok = True
for start in range(1, n + 1):
    if color[start]:
        continue
    color[start] = 1
    queue = deque([start])
    while queue and ok:
        cur = queue.popleft()
        for nb in adj[cur]:
            if color[nb] == 0:
                color[nb] = -color[cur]
                queue.append(nb)
            elif color[nb] == color[cur]:
                ok = False
                break
print("YES" if ok else "NO")
""",
        tests=[
            T(stdin="4 4\n1 2\n2 3\n3 4\n4 1\n", visible=True),
            T(stdin="3 3\n1 2\n2 3\n3 1\n", visible=True),
            T(stdin="5 5\n1 2\n2 3\n3 4\n4 5\n5 1\n", probe="edge:cycle"),
            T(stdin="6 3\n1 2\n3 4\n5 5\n", probe="edge:disconnected"),
            T(stdin="1 0\n", probe="edge:single"),
            T(stdin="3 3\n1 2\n2 3\n1 3\n", probe="adversarial:worst-case"),
            T(stdin="4 0\n", probe="edge:empty"),
            T(
                gen=lambda rng: _graph_case(
                    100000, [f"{rng.randint(1, 50000)} {rng.randint(50001, 100000)}" for _ in range(150000)]
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L28 (medium-hard, greedy) ----------------
    Q(
        qid="L28-A",
        level=28,
        topic="greedy",
        title="Feast Scheduling",
        time_limit_s=5,
        prompt="""
The great hall hosts one feast at a time. Feast i runs from s to e; a feast may
begin exactly when the previous ends. Maximize the number of feasts held.

Input: line 1: n (1 <= n <= 10^5). Then n lines "s e" (0 <= s < e <= 10^9).
Output: the maximum number of non-overlapping feasts.
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
n = int(data[0])
feasts = []
idx = 1
for _ in range(n):
    s, e = int(data[idx]), int(data[idx + 1])
    idx += 2
    feasts.append((e, s))
feasts.sort()
count = 0
free_at = -1
for e, s in feasts:
    if s >= free_at:
        count += 1
        free_at = e
print(count)
""",
        tests=[
            T(stdin="3\n1 3\n2 4\n3 5\n", visible=True),
            T(stdin="4\n1 2\n2 3\n3 4\n4 5\n", visible=True),
            T(stdin="3\n1 10\n2 3\n4 5\n", probe="adversarial:worst-case"),
            T(stdin="4\n5 8\n5 8\n5 8\n5 8\n", probe="edge:all-equal"),
            T(stdin="2\n1 5\n5 9\n", probe="edge:duplicates"),
            T(stdin="1\n0 1000000000\n", probe="edge:single"),
            T(stdin="5\n1 100\n1 100\n50 60\n55 65\n60 70\n", probe="edge:max-bounds"),
            T(
                gen=lambda rng: "100000\n" + "".join(
                    (lambda s: f"{s} {s + rng.randint(1, 100)}\n")(rng.randint(0, 10**9 - 101)) for _ in range(100000)
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L28-B",
        level=28,
        topic="greedy",
        title="Royal Change",
        prompt="""
The royal mint stamps coins of 1, 5, 10 and 25 shillings. Pay the exact toll
with as few coins as possible.

Input: one integer toll (0 <= toll <= 10^18).
Output: the minimum number of coins. (Looping coin by coin will outlive the
kingdom; use arithmetic.)
""",
        solution=r"""
import sys
n = int(sys.stdin.read())
coins = 0
for c in (25, 10, 5, 1):
    coins += n // c
    n %= c
print(coins)
""",
        tests=[
            T(stdin="41\n", visible=True),
            T(stdin="99\n", visible=True),
            T(stdin="0\n", probe="edge:zero"),
            T(stdin="4\n", probe="edge:single"),
            T(stdin="1000000000000000000\n", probe="edge:max-bounds"),
            T(stdin="999999999999999999\n", probe="edge:overflow"),
            T(stdin="30\n", probe="edge:duplicates"),
            T(stdin="24\n", probe="adversarial:worst-case"),
        ],
    ),
    # ---------------- L29 (medium-hard, graphs/grid) ----------------
    Q(
        qid="L29-A",
        level=29,
        topic="graphs",
        title="Isles of the Sunken Keep",
        time_limit_s=5,
        prompt="""
The flooded keep's map marks stone (#) and water (.). Stones touching north,
south, east or west form one isle - diagonals do not connect. Count the isles.

Input: line 1: r c (1 <= r, c <= 1000). Then r lines of c characters.
Output: the number of isles.
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.read().split()
r, c = int(data[0]), int(data[1])
grid = [list(row) for row in data[2:2 + r]]
count = 0
for i in range(r):
    for j in range(c):
        if grid[i][j] == '#':
            count += 1
            queue = deque([(i, j)])
            grid[i][j] = '.'
            while queue:
                x, y = queue.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < r and 0 <= ny < c and grid[nx][ny] == '#':
                        grid[nx][ny] = '.'
                        queue.append((nx, ny))
print(count)
""",
        tests=[
            T(stdin="4 5\n##..#\n##..#\n..#..\n#..##\n", visible=True),
            T(stdin="3 3\n###\n#.#\n###\n", visible=True),
            T(stdin="2 3\n...\n...\n", probe="edge:empty"),
            T(stdin="3 3\n###\n###\n###\n", probe="edge:max-bounds"),
            T(stdin="3 3\n#.#\n.#.\n#.#\n", probe="adversarial:worst-case"),
            T(stdin="1 1\n#\n", probe="edge:single"),
            T(stdin="2 4\n#.#.\n.#.#\n", probe="edge:duplicates"),
            T(gen=lambda rng: _grid(rng, 1000, 1000, 0.45), probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L29-B",
        level=29,
        topic="graphs",
        title="Tide of Torchfire",
        time_limit_s=5,
        prompt="""
Fire spreads from the tile (r0, c0) through its 4-connected region of oil (#).
Water (.) never burns. How many tiles burn in total?

Input: line 1: r c r0 c0 (1-based start, guaranteed oil). Then r lines of c
characters. 1 <= r, c <= 1000.
Output: the size of the burned region.
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.read().split()
r, c, r0, c0 = int(data[0]), int(data[1]), int(data[2]) - 1, int(data[3]) - 1
grid = [list(row) for row in data[4:4 + r]]
queue = deque([(r0, c0)])
grid[r0][c0] = '.'
burned = 0
while queue:
    x, y = queue.popleft()
    burned += 1
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < r and 0 <= ny < c and grid[nx][ny] == '#':
            grid[nx][ny] = '.'
            queue.append((nx, ny))
print(burned)
""",
        tests=[
            T(stdin="3 4 2 2\n#...\n###.\n..#.\n", visible=True),
            T(stdin="2 2 1 1\n##\n##\n", visible=True),
            T(stdin="3 3 2 2\n...\n.#.\n...\n", probe="edge:single"),
            T(stdin="2 5 1 1\n#####\n#####\n", probe="edge:max-bounds"),
            T(stdin="3 5 1 1\n##..#\n.#..#\n##..#\n", probe="adversarial:worst-case"),
            T(stdin="1 4 1 2\n####\n", probe="edge:unbalanced"),
            T(stdin="4 4 4 4\n#..#\n....\n..##\n..##\n", probe="edge:duplicates"),
            T(
                gen=lambda rng: (lambda body: "1000 1000 1 1\n#" + body[1:])(
                    _grid(rng, 1000, 1000, 0.6).split("\n", 1)[1]
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L30 BOSS x2 (hard) ----------------
    Q(
        qid="L30-B1",
        level=30,
        topic="graphs",
        title="Rite of Precedence",
        is_boss=True,
        time_limit_s=5,
        prompt="""
BOSS. The coronation demands every rite happen after all rites it depends on.
Among all lawful orders, the herald must proclaim the LEXICOGRAPHICALLY SMALLEST
(rites are numbered 1..n). If the dependencies knot into a cycle, proclaim
IMPOSSIBLE.

Input: line 1: n m (1 <= n <= 10^5, 0 <= m <= 2*10^5). Then m lines "u v": rite
u must precede rite v.
Output: the order as n space-separated numbers, or IMPOSSIBLE.
""",
        solution=r"""
import sys
import heapq
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
adj = [[] for _ in range(n + 1)]
indeg = [0] * (n + 1)
idx = 2
for _ in range(m):
    u, v = int(data[idx]), int(data[idx + 1])
    idx += 2
    adj[u].append(v)
    indeg[v] += 1
heap = [i for i in range(1, n + 1) if indeg[i] == 0]
heapq.heapify(heap)
order = []
while heap:
    cur = heapq.heappop(heap)
    order.append(cur)
    for nb in adj[cur]:
        indeg[nb] -= 1
        if indeg[nb] == 0:
            heapq.heappush(heap, nb)
print(" ".join(map(str, order)) if len(order) == n else "IMPOSSIBLE")
""",
        tests=[
            T(stdin="4 3\n1 2\n3 2\n2 4\n", visible=True),
            T(stdin="3 3\n1 2\n2 3\n3 1\n", visible=True),
            T(stdin="5 4\n5 4\n4 3\n3 2\n2 1\n", visible=True),
            T(stdin="4 2\n2 1\n4 3\n", probe="adversarial:worst-case"),
            T(stdin="6 2\n2 1\n5 6\n", probe="edge:disconnected"),
            T(stdin="1 0\n", probe="edge:single"),
            T(stdin="3 4\n1 2\n1 2\n2 3\n2 3\n", probe="edge:duplicates"),
            T(stdin="2 2\n1 2\n2 1\n", probe="edge:cycle"),
            T(
                gen=lambda rng: _graph_case(100000, [f"{i} {i + 1}" for i in range(1, 100000)]),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L30-B2",
        level=30,
        topic="dynamic-programming",
        title="The Quartermaster's Dilemma",
        is_boss=True,
        time_limit_s=5,
        prompt="""
BOSS. The quartermaster's wagon bears at most W stone of weight. Each relic has
a weight and a worth, and there is exactly one of each. Load the wagon for
maximum worth.

Input: line 1: n W (1 <= n <= 100, 0 <= W <= 10^4). Then n lines "weight worth"
(1 <= weight <= 10^4, 1 <= worth <= 10^9).
Output: the maximum total worth.
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
n, W = int(data[0]), int(data[1])
dp = [0] * (W + 1)
idx = 2
for _ in range(n):
    w, val = int(data[idx]), int(data[idx + 1])
    idx += 2
    for cap in range(W, w - 1, -1):
        cand = dp[cap - w] + val
        if cand > dp[cap]:
            dp[cap] = cand
print(dp[W])
""",
        tests=[
            T(stdin="3 50\n10 60\n20 100\n30 120\n", visible=True),
            T(stdin="4 5\n1 10\n2 20\n3 30\n4 40\n", visible=True),
            T(stdin="2 0\n5 100\n3 50\n", probe="edge:zero"),
            T(stdin="3 4\n5 100\n6 200\n7 300\n", probe="edge:no-solution"),
            T(stdin="1 10\n10 999\n", probe="edge:single"),
            T(stdin="3 60\n10 60\n20 100\n30 120\n", probe="edge:max-bounds"),
            T(stdin="4 6\n3 30\n3 30\n3 30\n3 30\n", probe="edge:all-equal"),
            T(stdin="3 10\n6 30\n5 20\n5 20\n", probe="adversarial:worst-case"),
            T(
                gen=lambda rng: f"100 10000\n" + "".join(
                    f"{rng.randint(1, 10000)} {rng.randint(1, 10**9)}\n" for _ in range(100)
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L31 (hard, graphs) ----------------
    Q(
        qid="L31-A",
        level=31,
        topic="graphs",
        title="Paths of Weighted Sorrow",
        time_limit_s=5,
        prompt="""
Every corridor exacts a toll of sorrow (bidirectional, non-negative). Find the
least total sorrow from chamber s to chamber t.

Input: line 1: n m s t (1 <= n <= 10^5, 0 <= m <= 2*10^5). Then m lines "u v w"
(0 <= w <= 10^6; parallel corridors possible).
Output: the minimum cost, or -1 if t is unreachable.
""",
        solution=r"""
import sys
import heapq
data = sys.stdin.buffer.read().split()
n, m, s, t = (int(x) for x in data[:4])
adj = [[] for _ in range(n + 1)]
idx = 4
for _ in range(m):
    u, v, w = int(data[idx]), int(data[idx + 1]), int(data[idx + 2])
    idx += 3
    adj[u].append((v, w))
    adj[v].append((u, w))
INF = float('inf')
dist = [INF] * (n + 1)
dist[s] = 0
heap = [(0, s)]
while heap:
    d, cur = heapq.heappop(heap)
    if d > dist[cur]:
        continue
    if cur == t:
        break
    for nb, w in adj[cur]:
        nd = d + w
        if nd < dist[nb]:
            dist[nb] = nd
            heapq.heappush(heap, (nd, nb))
print(dist[t] if dist[t] != INF else -1)
""",
        tests=[
            T(stdin="5 6 1 5\n1 2 2\n2 5 9\n1 3 1\n3 4 3\n4 5 2\n2 3 4\n", visible=True),
            T(stdin="3 3 1 3\n1 2 5\n2 3 5\n1 3 20\n", visible=True),
            T(stdin="4 2 1 4\n1 2 3\n3 4 1\n", probe="edge:no-solution"),
            T(stdin="3 2 1 3\n1 2 0\n2 3 0\n", probe="edge:zero"),
            T(stdin="3 4 1 3\n1 2 10\n1 2 1\n2 3 10\n2 3 1\n", probe="edge:duplicates"),
            T(stdin="2 1 1 1\n1 2 5\n", probe="edge:single"),
            T(stdin="4 4 1 4\n1 4 100\n1 2 1\n2 3 1\n3 4 1\n", probe="adversarial:worst-case"),
            T(
                gen=lambda rng: _graph_case(
                    50000,
                    [f"{i} {i + 1} {rng.randint(0, 10**6)}" for i in range(1, 50000)]
                    + edge_list(rng, 50000, 100000, weighted=(0, 10**6)),
                ).replace("\n", " 1 50000\n", 1),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L31-B",
        level=31,
        topic="graphs",
        title="Rot in the Granary",
        time_limit_s=5,
        prompt="""
Rot (R) spreads each night to every fresh sack (F) directly north, south, east
or west. Empty floor (.) stops nothing but holds no grain. After how many nights
is every sack rotten - or is some sack forever safe?

Input: line 1: r c (1 <= r, c <= 1000). Then r rows of {R, F, .}.
Output: the number of nights until no fresh sack remains (0 if none fresh at
the start), or -1 if some sack can never rot.
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.read().split()
r, c = int(data[0]), int(data[1])
grid = [list(row) for row in data[2:2 + r]]
queue = deque()
fresh = 0
for i in range(r):
    for j in range(c):
        if grid[i][j] == 'R':
            queue.append((i, j, 0))
        elif grid[i][j] == 'F':
            fresh += 1
nights = 0
while queue:
    x, y, d = queue.popleft()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < r and 0 <= ny < c and grid[nx][ny] == 'F':
            grid[nx][ny] = 'R'
            fresh -= 1
            nights = d + 1
            queue.append((nx, ny, d + 1))
print(-1 if fresh else nights)
""",
        tests=[
            T(stdin="3 3\nRF.\nFF.\n.FF\n", visible=True),
            T(stdin="2 2\nRF\nFF\n", visible=True),
            T(stdin="2 3\nR..\n...\n", probe="edge:zero"),
            T(stdin="3 3\nR.F\n...\n...\n", probe="edge:no-solution"),
            T(stdin="2 2\nRR\nRR\n", probe="edge:all-equal"),
            T(stdin="1 5\nRFFFF\n", probe="edge:unbalanced"),
            T(stdin="3 5\nR....\n.....\n....F\n", probe="adversarial:worst-case"),
            T(
                gen=lambda rng: "1000 1000\n" + "\n".join(
                    "".join("R" if (i == 0 and j == 0) else "F" for j in range(1000)) for i in range(1000)
                ) + "\n",
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L32 (hard, dynamic-programming) ----------------
    Q(
        qid="L32-A",
        level=32,
        topic="dynamic-programming",
        title="Scribe's Correction",
        time_limit_s=5,
        prompt="""
The apprentice miscopied a spell. Each correction inserts, deletes or replaces
one letter. How few corrections restore the master's text?

Input: two lines: the apprentice's copy and the master's text, each 0..2000
lowercase letters. An empty line means an empty string; the two lines are
always present.
Output: the minimum number of edits.
""",
        solution=r"""
import sys
lines = sys.stdin.read().split("\n")
a = lines[0].strip() if len(lines) > 0 else ""
b = lines[1].strip() if len(lines) > 1 else ""
n, m = len(a), len(b)
prev = list(range(m + 1))
for i in range(1, n + 1):
    cur = [i] + [0] * m
    for j in range(1, m + 1):
        cur[j] = min(
            prev[j] + 1,
            cur[j - 1] + 1,
            prev[j - 1] + (a[i - 1] != b[j - 1]),
        )
    prev = cur
print(prev[m])
""",
        tests=[
            T(stdin="horse\nros\n", visible=True),
            T(stdin="intention\nexecution\n", visible=True),
            T(stdin="\nspell\n", probe="edge:empty"),
            T(stdin="rune\nrune\n", probe="edge:zero"),
            T(stdin="abc\nxyz\n", probe="edge:max-bounds"),
            T(stdin="fire\nfires\n", probe="adversarial:worst-case"),
            T(stdin="a\nb\n", probe="edge:single"),
            T(
                gen=lambda rng: "".join(rng.choice("ab") for _ in range(2000)) + "\n" + "".join(rng.choice("ab") for _ in range(2000)) + "\n",
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L32-B",
        level=32,
        topic="dynamic-programming",
        title="Twin Chronicles",
        time_limit_s=5,
        prompt="""
Two chronicles describe the same war. The truth is the longest sequence of
events appearing in BOTH, in order (not necessarily adjacent). How long is it?

Input: two lines of 1..2000 lowercase letters.
Output: the length of the longest common subsequence.
""",
        solution=r"""
import sys
a, b = sys.stdin.read().split()
n, m = len(a), len(b)
prev = [0] * (m + 1)
for i in range(1, n + 1):
    cur = [0] * (m + 1)
    ai = a[i - 1]
    for j in range(1, m + 1):
        if ai == b[j - 1]:
            cur[j] = prev[j - 1] + 1
        else:
            cur[j] = cur[j - 1] if cur[j - 1] >= prev[j] else prev[j]
    prev = cur
print(prev[m])
""",
        tests=[
            T(stdin="abcde\nace\n", visible=True),
            T(stdin="warhammer\nhammerfall\n", visible=True),
            T(stdin="abc\nxyz\n", probe="edge:no-solution"),
            T(stdin="ember\nember\n", probe="edge:max-bounds"),
            T(stdin="a\na\n", probe="edge:single"),
            T(stdin="aabbaabb\nababab\n", probe="edge:duplicates"),
            T(stdin="abababab\nbabababa\n", probe="adversarial:worst-case"),
            T(
                gen=lambda rng: "".join(rng.choice("abc") for _ in range(2000)) + "\n" + "".join(rng.choice("abc") for _ in range(2000)) + "\n",
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L33 (hard, dynamic-programming) ----------------
    Q(
        qid="L33-A",
        level=33,
        topic="dynamic-programming",
        title="Arbitrary Coinage",
        time_limit_s=5,
        prompt="""
Foreign mints stamp coins of arbitrary values. Pay the toll exactly with the
fewest coins (unlimited supply of each), or admit it cannot be done.

Input: line 1: k and toll (1 <= k <= 50, 0 <= toll <= 10^5). Line 2: k coin
values (1 <= v <= 10^5).
Output: the minimum number of coins, or -1. (Greedy fails here; remember level
28 fondly.)
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
k, toll = int(data[0]), int(data[1])
coins = list(map(int, data[2:2 + k]))
INF = float('inf')
dp = [0] + [INF] * toll
for amount in range(1, toll + 1):
    for c in coins:
        if c <= amount and dp[amount - c] + 1 < dp[amount]:
            dp[amount] = dp[amount - c] + 1
print(dp[toll] if dp[toll] != INF else -1)
""",
        tests=[
            T(stdin="3 11\n1 2 5\n", visible=True),
            T(stdin="3 6\n1 3 4\n", visible=True),
            T(stdin="2 7\n2 4\n", probe="edge:no-solution"),
            T(stdin="1 0\n3\n", probe="edge:zero"),
            T(stdin="1 9\n3\n", probe="edge:single"),
            T(stdin="3 6\n4 3 1\n", probe="adversarial:worst-case"),
            T(stdin="4 10\n5 5 5 5\n", probe="edge:duplicates"),
            T(gen=lambda rng: f"50 100000\n{' '.join(str(rng.randint(1, 100000)) for _ in range(49))} 7\n", probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L33-B",
        level=33,
        topic="dynamic-programming",
        title="Silent Plunder",
        time_limit_s=4,
        prompt="""
The houses of Hushed Row stand in a line; robbing two ADJACENT houses wakes the
watch. Plunder the maximum gold.

Input: line 1: n (1 <= n <= 10^5). Line 2: n non-negative amounts (<= 10^9).
Output: the maximum total without robbing adjacent houses.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
take, skip = 0, 0
for tok in data[1:1 + n]:
    v = int(tok)
    take, skip = skip + v, max(skip, take)
print(max(take, skip))
""",
        tests=[
            T(stdin="4\n1 2 3 1\n", visible=True),
            T(stdin="5\n2 7 9 3 1\n", visible=True),
            T(stdin="1\n5\n", probe="edge:single"),
            T(stdin="4\n6 6 6 6\n", probe="edge:all-equal"),
            T(stdin="6\n100 1 1 100 1 100\n", probe="adversarial:worst-case"),
            T(stdin="3\n0 0 0\n", probe="edge:zero"),
            T(stdin="2\n5 10\n", probe="edge:duplicates"),
            T(gen=gen_arr(100000, 0, 10**9), probe="perf:large_n"),
        ],
    ),
    # ---------------- L34 (hard, graphs) ----------------
    Q(
        qid="L34-A",
        level=34,
        topic="graphs",
        title="Provinces of the Deep",
        time_limit_s=5,
        prompt="""
The deep-dwellers report which settlements trade directly, as an n x n matrix
(symmetric, 1 = direct trade). Settlements trading through intermediaries share
a province. Count the provinces.

Input: line 1: n (1 <= n <= 1000). Then n rows of n digits (0/1, no spaces).
Output: the number of provinces.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
rows = data[1:1 + n]
parent = list(range(n))

def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

for i in range(n):
    row = rows[i]
    for j in range(i + 1, n):
        if row[j] == '1':
            ri, rj = find(i), find(j)
            if ri != rj:
                parent[ri] = rj
print(len({find(i) for i in range(n)}))
""",
        tests=[
            T(stdin="3\n110\n110\n001\n", visible=True),
            T(stdin="3\n100\n010\n001\n", visible=True),
            T(stdin="4\n1000\n0100\n0010\n0001\n", probe="edge:disconnected"),
            T(stdin="4\n1111\n1111\n1111\n1111\n", probe="edge:max-bounds"),
            T(stdin="1\n1\n", probe="edge:single"),
            T(stdin="4\n1100\n1110\n0111\n0011\n", probe="adversarial:worst-case"),
            T(stdin="2\n11\n11\n", probe="edge:duplicates"),
            T(
                gen=lambda rng: (lambda n: f"{n}\n" + "\n".join(
                    "".join("1" if i == j or abs(i - j) == 1 else "0" for j in range(n)) for i in range(n)
                ) + "\n")(1000),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L34-B",
        level=34,
        topic="graphs",
        title="Cheapest Web of Roads",
        time_limit_s=5,
        prompt="""
The council will pave just enough roads to connect every town, spending as
little as possible. Quote the minimum total cost.

Input: line 1: n m (1 <= n <= 10^5, 0 <= m <= 2*10^5). Then m lines "u v w"
(0 <= w <= 10^6; parallel roads possible).
Output: the total weight of a minimum spanning tree, or -1 if the towns cannot
all be connected.
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
edges = []
idx = 2
for _ in range(m):
    u, v, w = int(data[idx]), int(data[idx + 1]), int(data[idx + 2])
    idx += 3
    edges.append((w, u, v))
edges.sort()
parent = list(range(n + 1))

def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

total = 0
used = 0
for w, u, v in edges:
    ru, rv = find(u), find(v)
    if ru != rv:
        parent[ru] = rv
        total += w
        used += 1
print(total if used == n - 1 else -1)
""",
        tests=[
            T(stdin="4 5\n1 2 1\n2 3 2\n3 4 3\n4 1 4\n1 3 5\n", visible=True),
            T(stdin="3 3\n1 2 10\n2 3 10\n1 3 10\n", visible=True),
            T(stdin="4 2\n1 2 1\n3 4 1\n", probe="edge:disconnected"),
            T(stdin="3 4\n1 2 5\n1 2 1\n2 3 5\n2 3 1\n", probe="edge:duplicates"),
            T(stdin="3 3\n1 2 0\n2 3 0\n1 3 0\n", probe="edge:zero"),
            T(stdin="1 0\n", probe="edge:single"),
            T(stdin="4 6\n1 2 1\n2 3 1\n3 4 1\n1 3 1\n2 4 1\n1 4 1\n", probe="edge:cycle"),
            T(
                gen=lambda rng: _graph_case(
                    100000,
                    [f"{i} {i + 1} {rng.randint(0, 10**6)}" for i in range(1, 100000)]
                    + edge_list(rng, 100000, 100000, weighted=(0, 10**6)),
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L35 BOSS x2 (hard) ----------------
    Q(
        qid="L35-B1",
        level=35,
        topic="graphs",
        title="Chant of Transformation",
        is_boss=True,
        time_limit_s=5,
        prompt="""
BOSS. One word becomes another by changing a single letter at a time, and every
intermediate word must appear in the grimoire. Count the words in the shortest
chant from start to target (both included). Start is always lawful; target must
be in the grimoire.

Input: line 1: d (1 <= d <= 5000) - grimoire size. Line 2: start and target
(lowercase, equal length 1..10). Then d lines: the grimoire's words (same
length).
Output: the length of the shortest chant, or -1. If start equals target the
chant has length 1.
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.read().split()
d = int(data[0])
start, target = data[1], data[2]
words = set(data[3:3 + d])
if start == target and target in words:
    print(1)
else:
    if target not in words:
        print(-1)
    else:
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        dist = {start: 1}
        queue = deque([start])
        ans = -1
        while queue:
            word = queue.popleft()
            if word == target:
                ans = dist[word]
                break
            for i in range(len(word)):
                for ch in alphabet:
                    if ch == word[i]:
                        continue
                    cand = word[:i] + ch + word[i + 1:]
                    if cand in words and cand not in dist:
                        dist[cand] = dist[word] + 1
                        queue.append(cand)
        print(ans)
""",
        tests=[
            T(stdin="6\nhit cog\nhot dot dog lot log cog\n", visible=True),
            T(stdin="5\nhit cog\nhot dot dog lot log\n", visible=True),
            T(stdin="3\nabc abc\nabc abd abe\n", probe="edge:zero"),
            T(stdin="2\naa bb\nab bb\n", probe="edge:single"),
            T(stdin="4\ncold warm\ncord ward worm word\n", probe="edge:no-solution"),
            T(stdin="6\nred tan\nted tad tan rad rex ted\n", probe="edge:duplicates"),
            T(stdin="8\naaa ccc\naac aca caa acc cac cca ccc aaa\n", probe="adversarial:worst-case"),
            T(stdin="3\nxy yy\nzz yy xx\n", probe="edge:disconnected"),
            T(
                gen=lambda rng: (lambda words: f"{len(words)}\n{words[0]} {words[-1]}\n{' '.join(words)}\n")(
                    sorted({"".join(rng.choice("abc") for _ in range(6)) for _ in range(5000)})
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    Q(
        qid="L35-B2",
        level=35,
        topic="dynamic-programming",
        title="Order of the Golden Chain",
        is_boss=True,
        time_limit_s=5,
        prompt="""
BOSS. n golden plates must be fused in a chain. Fusing an a x b plate with a
b x c plate costs a*b*c embers and yields an a x c plate. Choose the fusing
order that spends the fewest embers.

Input: line 1: n (1 <= n <= 200) - the number of plates. Line 2: n+1 integers
d0..dn (1 <= d <= 500); plate i is d(i-1) x d(i).
Output: the minimum total embers.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
dims = list(map(int, data[1:2 + n]))
INF = float('inf')
dp = [[0] * (n + 1) for _ in range(n + 1)]
for length in range(2, n + 1):
    for i in range(1, n - length + 2):
        j = i + length - 1
        best = INF
        for k in range(i, j):
            cand = dp[i][k] + dp[k + 1][j] + dims[i - 1] * dims[k] * dims[j]
            if cand < best:
                best = cand
        dp[i][j] = best
print(dp[1][n])
""",
        tests=[
            T(stdin="3\n10 30 5 60\n", visible=True),
            T(stdin="3\n1 2 3 4\n", visible=True),
            T(stdin="1\n7 9\n", probe="edge:single"),
            T(stdin="4\n5 5 5 5 5\n", probe="edge:all-equal"),
            T(stdin="4\n1 100 1 100 1\n", probe="adversarial:worst-case"),
            T(stdin="2\n1 1 1\n", probe="edge:zero"),
            T(stdin="5\n10 20 30 40 30 20\n", probe="edge:max-bounds"),
            T(gen=lambda rng: f"200\n{' '.join(str(rng.randint(1, 500)) for _ in range(201))}\n", probe="perf:large_n"),
        ],
    ),
    # ---------------- L36 (hard, dynamic-programming) ----------------
    Q(
        qid="L36-A",
        level=36,
        topic="dynamic-programming",
        title="Equal Split of Spoils",
        time_limit_s=5,
        prompt="""
Two rival captains will only stand down if the plunder can be split into two
piles of EXACTLY equal value. Can it?

Input: line 1: n (1 <= n <= 200). Line 2: n values (1 <= v <= 100).
Output: YES if the multiset splits into two equal-sum halves, else NO.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
vals = list(map(int, data[1:1 + n]))
total = sum(vals)
if total % 2:
    print("NO")
else:
    target = total // 2
    reachable = 1
    for v in vals:
        reachable |= reachable << v
    print("YES" if (reachable >> target) & 1 else "NO")
""",
        tests=[
            T(stdin="4\n1 5 11 5\n", visible=True),
            T(stdin="4\n1 2 3 5\n", visible=True),
            T(stdin="3\n1 1 1\n", probe="edge:no-solution"),
            T(stdin="4\n7 7 7 7\n", probe="edge:all-equal"),
            T(stdin="1\n10\n", probe="edge:single"),
            T(stdin="6\n3 3 3 3 5 1\n", probe="adversarial:worst-case"),
            T(stdin="2\n50 50\n", probe="edge:duplicates"),
            T(gen=lambda rng: arr_case([rng.randint(1, 100) for _ in range(200)]), probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L36-B",
        level=36,
        topic="dynamic-programming",
        title="Warded Passages",
        time_limit_s=5,
        prompt="""
From the north-west cell to the south-east cell, moving only south or east,
count the distinct routes that avoid warded cells (#), modulo 1000000007.

Input: line 1: r c (1 <= r, c <= 1000). Then r rows of {., #}.
Output: the number of routes mod 1000000007 (0 if none, including when either
corner is warded).
""",
        solution=r"""
import sys
MOD = 1000000007
data = sys.stdin.read().split()
r, c = int(data[0]), int(data[1])
grid = data[2:2 + r]
dp = [0] * c
dp[0] = 1 if grid[0][0] == '.' else 0
for i in range(r):
    row = grid[i]
    for j in range(c):
        if row[j] == '#':
            dp[j] = 0
        elif j > 0:
            dp[j] = (dp[j] + dp[j - 1]) % MOD
print(dp[c - 1])
""",
        tests=[
            T(stdin="3 3\n...\n.#.\n...\n", visible=True),
            T(stdin="2 2\n..\n..\n", visible=True),
            T(stdin="2 2\n#.\n..\n", probe="edge:empty"),
            T(stdin="3 3\n...\n...\n...\n", probe="edge:max-bounds"),
            T(stdin="3 3\n...\n###\n...\n", probe="edge:no-solution"),
            T(stdin="1 1\n.\n", probe="edge:single"),
            T(stdin="2 5\n....#\n#....\n", probe="adversarial:worst-case"),
            T(
                gen=lambda rng: f"1000 1000\n" + "\n".join(
                    "".join("#" if (rng.random() < 0.05 and not (i == 0 and j == 0) and not (i == 999 and j == 999)) else "." for j in range(1000))
                    for i in range(1000)
                ) + "\n",
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L37 (hard, greedy) ----------------
    Q(
        qid="L37-A",
        level=37,
        topic="greedy",
        title="Leaps of Faith",
        time_limit_s=4,
        prompt="""
Each rune tile tells you the FARTHEST number of tiles you may leap from it.
Starting on tile 1, reach tile n in the fewest leaps.

Input: line 1: n (1 <= n <= 10^5). Line 2: n non-negative leap limits (<= n).
Output: the minimum number of leaps, or -1 if tile n is unreachable. Standing
on tile n already costs 0 leaps.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
vals = list(map(int, data[1:1 + n]))
if n == 1:
    print(0)
else:
    jumps = 0
    cur_end = 0
    far = 0
    ans = -1
    for i in range(n - 1):
        if i > far:
            break
        far = max(far, i + vals[i])
        if i == cur_end:
            jumps += 1
            cur_end = far
            if cur_end >= n - 1:
                ans = jumps
                break
    print(ans)
""",
        tests=[
            T(stdin="5\n2 3 1 1 4\n", visible=True),
            T(stdin="5\n3 2 1 0 4\n", visible=True),
            T(stdin="1\n0\n", probe="edge:single"),
            T(stdin="4\n1 0 1 1\n", probe="edge:no-solution"),
            T(stdin="5\n1 1 1 1 1\n", probe="edge:all-equal"),
            T(stdin="6\n5 4 3 2 1 0\n", probe="adversarial:worst-case"),
            T(stdin="3\n0 1 1\n", probe="edge:zero"),
            T(gen=lambda rng: arr_case([rng.randint(1, 3) for _ in range(100000)]), probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L37-B",
        level=37,
        topic="greedy",
        title="Circuit of Embers",
        time_limit_s=4,
        prompt="""
n braziers stand in a ring. Brazier i grants gas[i] embers; the march to the
next brazier costs cost[i]. Starting empty at some brazier, complete one full
clockwise circuit. Find the unique starting brazier, or report -1.

Input: line 1: n (1 <= n <= 10^5). Line 2: n gains. Line 3: n costs
(0 <= v <= 10^9).
Output: the 1-based starting index, or -1 if no start completes the circuit.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
gas = list(map(int, data[1:1 + n]))
cost = list(map(int, data[1 + n:1 + 2 * n]))
if sum(gas) < sum(cost):
    print(-1)
else:
    tank = 0
    start = 0
    for i in range(n):
        tank += gas[i] - cost[i]
        if tank < 0:
            start = i + 1
            tank = 0
    print(start + 1)
""",
        tests=[
            T(stdin="5\n1 2 3 4 5\n3 4 5 1 2\n", visible=True),
            T(stdin="3\n2 3 4\n3 4 3\n", visible=True),
            T(stdin="3\n1 1 1\n2 2 2\n", probe="edge:no-solution"),
            T(stdin="4\n0 0 0 4\n1 1 1 1\n", probe="edge:max-bounds"),
            T(stdin="3\n5 5 5\n5 5 5\n", probe="edge:zero"),
            T(stdin="1\n9\n3\n", probe="edge:single"),
            T(stdin="4\n3 1 1 1\n1 1 1 3\n", probe="adversarial:worst-case"),
            T(
                gen=lambda rng: (lambda g, c: f"{len(g)}\n{' '.join(map(str, g))}\n{' '.join(map(str, c))}\n")(
                    [rng.randint(0, 100) for _ in range(100000)], [rng.randint(0, 99) for _ in range(100000)]
                ),
                probe="perf:large_n",
            ),
        ],
    ),
    # ---------------- L38 (hard, binary-search) ----------------
    Q(
        qid="L38-A",
        level=38,
        topic="binary-search",
        title="Stabling the Nightmares",
        time_limit_s=5,
        prompt="""
k nightmares must be stabled in n stalls along a corridor (positions given).
Nightmares stabled too close together feed on each other's terror. Maximize the
MINIMUM distance between any two stabled nightmares.

Input: line 1: n k (2 <= k <= n <= 10^5). Line 2: n stall positions
(0 <= p <= 10^9, duplicates possible).
Output: the largest possible minimum gap.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
pos = sorted(map(int, data[2:2 + n]))

def fits(gap):
    count = 1
    last = pos[0]
    for p in pos[1:]:
        if p - last >= gap:
            count += 1
            last = p
            if count >= k:
                return True
    return count >= k

lo, hi = 0, pos[-1] - pos[0]
while lo < hi:
    mid = (lo + hi + 1) // 2
    if fits(mid):
        lo = mid
    else:
        hi = mid - 1
print(lo)
""",
        tests=[
            T(stdin="5 3\n1 2 8 4 9\n", visible=True),
            T(stdin="4 2\n1 5 9 14\n", visible=True),
            T(stdin="3 2\n0 1000000000 500000000\n", probe="edge:max-bounds"),
            T(stdin="4 4\n1 2 3 4\n", probe="adversarial:worst-case"),
            T(stdin="5 3\n7 7 7 10 13\n", probe="edge:duplicates"),
            T(stdin="2 2\n3 3\n", probe="edge:zero"),
            T(stdin="6 2\n1 1 1 1 1 100\n", probe="edge:all-equal"),
            T(gen=lambda rng: arr_case(rand_ints(rng, 100000, 0, 10**9)).replace("\n", " 500\n", 1), probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L38-B",
        level=38,
        topic="binary-search",
        title="Burden Split",
        time_limit_s=5,
        prompt="""
The caravan's n crates (in fixed order) must be split among k porters, each
taking a CONTIGUOUS run. The strongest porter's load defines the day's misery.
Minimize it.

Input: line 1: n k (1 <= k <= n <= 10^5). Line 2: n crate weights
(0 <= w <= 10^6).
Output: the minimum possible maximum load.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
vals = list(map(int, data[2:2 + n]))

def parts_needed(cap):
    parts = 1
    cur = 0
    for v in vals:
        if cur + v > cap:
            parts += 1
            cur = v
        else:
            cur += v
    return parts

lo, hi = max(vals), sum(vals)
while lo < hi:
    mid = (lo + hi) // 2
    if parts_needed(mid) <= k:
        hi = mid
    else:
        lo = mid + 1
print(lo)
""",
        tests=[
            T(stdin="5 2\n7 2 5 10 8\n", visible=True),
            T(stdin="4 2\n1 2 3 4\n", visible=True),
            T(stdin="4 1\n5 5 5 5\n", probe="edge:max-bounds"),
            T(stdin="4 4\n9 1 9 1\n", probe="edge:single"),
            T(stdin="5 3\n4 4 4 4 4\n", probe="edge:all-equal"),
            T(stdin="5 2\n1 1 1 1 1000000\n", probe="edge:unbalanced"),
            T(stdin="3 2\n0 0 0\n", probe="edge:zero"),
            T(gen=lambda rng: arr_case(rand_ints(rng, 100000, 0, 10**6)).replace("\n", " 17\n", 1), probe="perf:large_n"),
        ],
    ),
    # ---------------- L39 (hard, dynamic-programming) ----------------
    Q(
        qid="L39-A",
        level=39,
        topic="dynamic-programming",
        title="Hall of Mirrors",
        time_limit_s=5,
        prompt="""
Somewhere in the inscription hides the longest mirror-phrase (palindromic
substring - contiguous). Report its length.

Input: one line of 1..5000 lowercase letters.
Output: the length of the longest palindromic substring.
""",
        solution=r"""
import sys
s = sys.stdin.read().strip()
n = len(s)
best = 1
for center in range(n):
    for lo, hi in ((center, center), (center, center + 1)):
        while lo >= 0 and hi < n and s[lo] == s[hi]:
            lo -= 1
            hi += 1
        best = max(best, hi - lo - 1)
print(best)
""",
        tests=[
            T(stdin="babad\n", visible=True),
            T(stdin="cbbd\n", visible=True),
            T(stdin="aaaa\n", probe="edge:all-equal"),
            T(stdin="abcdefg\n", probe="edge:single"),
            T(stdin="abacabad\n", probe="adversarial:worst-case"),
            T(stdin="xyzzyx\n", probe="edge:max-bounds"),
            T(stdin="aabbaa\n", probe="edge:duplicates"),
            T(gen=lambda rng: "".join(rng.choice("ab") for _ in range(5000)) + "\n", probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L39-B",
        level=39,
        topic="dynamic-programming",
        title="Cipher of Many Readings",
        time_limit_s=4,
        prompt="""
The cipher maps 1->a .. 26->z. A digit string may decode many ways ("12" is
"ab" or "l"). Count the decodings, modulo 1000000007. A reading that uses "0"
alone or "30" is void.

Input: one line of 1..10^5 digits.
Output: the number of valid decodings mod 1000000007 (0 if none).
""",
        solution=r"""
import sys
MOD = 1000000007
s = sys.stdin.read().strip()
n = len(s)
prev2, prev1 = 1, 1 if s[0] != '0' else 0
for i in range(1, n):
    cur = 0
    if s[i] != '0':
        cur = prev1
    two = int(s[i - 1:i + 1])
    if 10 <= two <= 26:
        cur = (cur + prev2) % MOD
    prev2, prev1 = prev1, cur
print(prev1)
""",
        tests=[
            T(stdin="226\n", visible=True),
            T(stdin="12\n", visible=True),
            T(stdin="06\n", probe="edge:zero"),
            T(stdin="10\n", probe="adversarial:worst-case"),
            T(stdin="30\n", probe="edge:no-solution"),
            T(stdin="7\n", probe="edge:single"),
            T(stdin="101010\n", probe="edge:duplicates"),
            T(gen=lambda rng: "1" * 100000 + "\n", probe="perf:large_n"),
        ],
    ),
    # ---------------- L40 BOSS x2 (hard, competitive style) ----------------
    Q(
        qid="L40-B1",
        level=40,
        topic="arrays",
        title="Ring of Greed",
        is_boss=True,
        time_limit_s=5,
        prompt="""
BOSS. The treasure ring is circular: choose a non-empty run of CONSECUTIVE
chambers - the run may wrap past the ring's seam - and take their sum. Some
chambers are cursed (negative). Maximize the take.

Input: line 1: n (1 <= n <= 2*10^5). Line 2: n integers, |v| <= 10^6.
Output: the maximum circular subarray sum.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
vals = list(map(int, data[1:1 + n]))
total = sum(vals)
best_straight = cur_max = vals[0]
worst = cur_min = vals[0]
for v in vals[1:]:
    cur_max = v + max(cur_max, 0)
    best_straight = max(best_straight, cur_max)
    cur_min = v + min(cur_min, 0)
    worst = min(worst, cur_min)
if best_straight < 0:
    print(best_straight)
else:
    print(max(best_straight, total - worst))
""",
        tests=[
            T(stdin="5\n1 -2 3 -2 5\n", visible=True),
            T(stdin="3\n5 -3 5\n", visible=True),
            T(stdin="3\n-3 -2 -3\n", probe="edge:negative"),
            T(stdin="4\n8 -1 -1 8\n", probe="adversarial:worst-case"),
            T(stdin="1\n-7\n", probe="edge:single"),
            T(stdin="4\n0 0 0 0\n", probe="edge:zero"),
            T(stdin="5\n2 2 2 2 2\n", probe="edge:all-equal"),
            T(stdin="6\n-1 40 -90 40 -1 1\n", probe="edge:max-bounds"),
            T(gen=gen_arr(200000, -10**6, 10**6), probe="perf:large_n"),
        ],
    ),
    Q(
        qid="L40-B2",
        level=40,
        topic="sliding-window",
        title="Watchers on the Parapet",
        is_boss=True,
        time_limit_s=5,
        prompt="""
BOSS. As the patrol window of width k slides along the parapet, report the
tallest watcher visible in each position.

Input: line 1: n k (1 <= k <= n <= 2*10^5). Line 2: n heights, |v| <= 10^9.
Output: the n-k+1 window maxima, space-separated. (Recomputing each window
maximum from scratch will be noticed - and punished.)
""",
        solution=r"""
import sys
from collections import deque
data = sys.stdin.buffer.read().split()
n, k = int(data[0]), int(data[1])
vals = list(map(int, data[2:2 + n]))
dq = deque()
out = []
for i, v in enumerate(vals):
    while dq and vals[dq[-1]] <= v:
        dq.pop()
    dq.append(i)
    if dq[0] <= i - k:
        dq.popleft()
    if i >= k - 1:
        out.append(vals[dq[0]])
print(" ".join(map(str, out)))
""",
        tests=[
            T(stdin="8 3\n1 3 -1 -3 5 3 6 7\n", visible=True),
            T(stdin="5 2\n4 3 2 1 5\n", visible=True),
            T(stdin="5 5\n2 9 1 8 3\n", probe="edge:max-bounds"),
            T(stdin="4 1\n7 2 9 4\n", probe="edge:single"),
            T(stdin="5 3\n6 6 6 6 6\n", probe="edge:all-equal"),
            T(stdin="6 2\n9 8 7 6 5 4\n", probe="edge:reverse-sorted"),
            T(stdin="6 2\n1 2 3 4 5 6\n", probe="edge:sorted"),
            T(gen=lambda rng: arr_case([(i % 3) * 7 - 3 for i in range(200000)]).replace("\n", " 500\n", 1), probe="adversarial:worst-case"),
            T(gen=lambda rng: arr_case(rand_ints(rng, 200000, -10**9, 10**9)).replace("\n", " 1000\n", 1), probe="perf:large_n"),
        ],
    ),
]

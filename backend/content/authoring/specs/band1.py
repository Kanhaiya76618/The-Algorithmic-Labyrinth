"""Levels 1-10: easy -> medium. Arrays, strings, hashing, two-pointers.

3-4 tests per question, 1-2 visible.
"""

from model import Q, T
from specs.helpers import arr_case, gen_arr, gen_word

QUESTIONS = [
    # ---------------- L1 (easy, arrays) ----------------
    Q(
        qid="L01-A",
        level=1,
        topic="arrays",
        title="Torchlit Tally",
        prompt="""
Fleeing adventurers dropped n coin piles in the entry hall. Count the whole hoard
before the torches gutter out.

Input: line 1: n (1 <= n <= 1000). Line 2: n integers, each |v| <= 10^6.
Output: one integer - the total value.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
print(sum(map(int, data[1:1 + n])))
""",
        tests=[
            T(stdin="5\n1 2 3 4 5\n", visible=True),
            T(stdin="3\n10 0 7\n", visible=True),
            T(stdin="1\n42\n", probe="edge:single"),
            T(stdin="4\n-5 -9 3 -1\n", probe="edge:negative"),
        ],
    ),
    Q(
        qid="L01-B",
        level=1,
        topic="arrays",
        title="Deepest Footprint",
        prompt="""
The mud of the entry hall records n footprints, each with a depth reading. Report
the deepest one - that is the beast you are following.

Input: line 1: n (1 <= n <= 1000). Line 2: n integers, each |v| <= 10^6.
Output: one integer - the maximum value.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
print(max(map(int, data[1:1 + n])))
""",
        tests=[
            T(stdin="5\n3 9 2 9 4\n", visible=True),
            T(stdin="4\n7 7 7 7\n", probe="edge:all-equal"),
            T(stdin="3\n-8 -2 -5\n", probe="edge:negative"),
            T(stdin="1\n-1000000\n", probe="edge:single"),
        ],
    ),
    # ---------------- L2 (easy, arrays) ----------------
    Q(
        qid="L02-A",
        level=2,
        topic="arrays",
        title="Trap Counter",
        prompt="""
Your dowsing rod hums at pressure plates heavier than the trigger weight t. Count
how many of the n floor tiles will spring a trap.

Input: line 1: n and t (1 <= n <= 1000, |t| <= 10^6). Line 2: n integers (tile
weights, |v| <= 10^6).
Output: one integer - the count of tiles with weight strictly greater than t.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n, t = int(data[0]), int(data[1])
vals = list(map(int, data[2:2 + n]))
print(sum(1 for v in vals if v > t))
""",
        tests=[
            T(stdin="5 10\n3 11 10 25 9\n", visible=True),
            T(stdin="4 100\n1 2 3 4\n", probe="edge:no-solution"),
            T(stdin="3 5\n5 5 5\n", probe="edge:all-equal"),
        ],
    ),
    Q(
        qid="L02-B",
        level=2,
        topic="arrays",
        title="Corridor Reversal",
        prompt="""
The corridor's rune sequence must be spoken backwards to unbar the door. Print the
runes in reverse order.

Input: line 1: n (1 <= n <= 1000). Line 2: n integers.
Output: the n integers in reverse order, space-separated on one line.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
vals = data[1:1 + n]
print(" ".join(reversed(vals)))
""",
        tests=[
            T(stdin="5\n1 2 3 4 5\n", visible=True),
            T(stdin="1\n9\n", probe="edge:single"),
            T(stdin="4\n2 2 3 3\n", probe="edge:duplicates"),
        ],
    ),
    # ---------------- L3 (easy, strings) ----------------
    Q(
        qid="L03-A",
        level=3,
        topic="strings",
        title="Mirror Rune",
        prompt="""
A mirror rune reads the same forwards and backwards, ignoring letter case. Decide
whether the inscription is a mirror rune.

Input: one line, an inscription of 1..1000 letters (a-z, A-Z).
Output: YES if it is a palindrome ignoring case, otherwise NO.
""",
        solution=r"""
import sys
s = sys.stdin.read().strip().lower()
print("YES" if s == s[::-1] else "NO")
""",
        tests=[
            T(stdin="LevEl\n", visible=True),
            T(stdin="dungeon\n", visible=True),
            T(stdin="X\n", probe="edge:single"),
            T(stdin="AbcCBa\n", probe="adversarial:worst-case"),
        ],
    ),
    Q(
        qid="L03-B",
        level=3,
        topic="strings",
        title="Vowel Harvest",
        prompt="""
Each vowel in the incantation feeds the lantern one breath of air. Count the vowels
(a, e, i, o, u - either case).

Input: one line of 1..1000 letters.
Output: one integer - the number of vowels.
""",
        solution=r"""
import sys
s = sys.stdin.read().strip().lower()
print(sum(1 for c in s if c in "aeiou"))
""",
        tests=[
            T(stdin="Labyrinth\n", visible=True),
            T(stdin="rhythms\n", probe="edge:no-solution"),
            T(stdin="AEIOU\n", probe="adversarial:worst-case"),
        ],
    ),
    # ---------------- L4 (easy, strings) ----------------
    Q(
        qid="L04-A",
        level=4,
        topic="strings",
        title="Echo Cipher",
        prompt="""
The echo of this cavern flips every letter's case and leaves everything else
untouched. Print what the cavern echoes back.

Input: one line of 1..1000 printable characters (no spaces).
Output: the line with each letter's case toggled.
""",
        solution=r"""
import sys
print(sys.stdin.read().strip().swapcase())
""",
        tests=[
            T(stdin="DungeonOfRecall\n", visible=True),
            T(stdin="x1y2Z3!\n", probe="adversarial:worst-case"),
            T(stdin="Q\n", probe="edge:single"),
        ],
    ),
    Q(
        qid="L04-B",
        level=4,
        topic="strings",
        title="Lone Sigil",
        prompt="""
Only a sigil that appears exactly once in the inscription can be traced safely.
Find the first such sigil, reading left to right.

Input: one line of 1..1000 lowercase letters.
Output: the first character that occurs exactly once, or NONE if every character
repeats.
""",
        solution=r"""
import sys
from collections import Counter
s = sys.stdin.read().strip()
counts = Counter(s)
for c in s:
    if counts[c] == 1:
        print(c)
        break
else:
    print("NONE")
""",
        tests=[
            T(stdin="torchbearer\n", visible=True),
            T(stdin="abcabc\n", probe="edge:no-solution"),
            T(stdin="zzzz\n", probe="edge:all-equal"),
        ],
    ),
    # ---------------- L5 BOSS (easy-medium, hashing) ----------------
    Q(
        qid="L05-B1",
        level=5,
        topic="hashing",
        title="Gatekeeper of Pairs",
        is_boss=True,
        prompt="""
BOSS. The gate bears two keyholes and a carved sum. You hold n keys; the gate opens
only if two DIFFERENT keys add up exactly to the carved sum. Tell the Gatekeeper
whether it must let you pass.

Input: line 1: n and target (2 <= n <= 10^5, |target| <= 2*10^9). Line 2: n integers,
each |v| <= 10^9.
Output: YES if some pair of distinct positions sums to target, else NO.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n, target = int(data[0]), int(data[1])
seen = set()
ok = False
for tok in data[2:2 + n]:
    v = int(tok)
    if target - v in seen:
        ok = True
        break
    seen.add(v)
print("YES" if ok else "NO")
""",
        tests=[
            T(stdin="5 9\n2 7 11 15 1\n", visible=True),
            T(stdin="4 100\n1 2 3 4\n", probe="edge:no-solution"),
            T(stdin="3 6\n3 5 3\n", probe="edge:duplicates"),
            T(stdin="4 -8\n-3 -5 2 10\n", probe="edge:negative"),
        ],
    ),
    # ---------------- L6 (easy-medium, hashing) ----------------
    Q(
        qid="L06-A",
        level=6,
        topic="hashing",
        title="Twin Wards",
        prompt="""
Two identical ward-stones anywhere in the hall cancel each other and drop the
barrier. Do the n ward-stones contain any duplicate value?

Input: line 1: n (1 <= n <= 10^5). Line 2: n integers, |v| <= 10^9.
Output: YES if any value appears at least twice, else NO.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
vals = data[1:1 + n]
print("YES" if len(set(vals)) < n else "NO")
""",
        tests=[
            T(stdin="5\n3 1 4 1 5\n", visible=True),
            T(stdin="4\n10 20 30 40\n", probe="edge:no-solution"),
            T(stdin="6\n9 1 2 3 4 9\n", probe="edge:duplicates"),
        ],
    ),
    Q(
        qid="L06-B",
        level=6,
        topic="hashing",
        title="Dominant Ingredient",
        prompt="""
The cauldron takes on the flavour of whichever ingredient id appears most often.
On a tie, the smallest id wins (old kitchen law).

Input: line 1: n (1 <= n <= 10^5). Line 2: n ingredient ids (0 <= id <= 10^9).
Output: the dominant ingredient id.
""",
        solution=r"""
import sys
from collections import Counter
data = sys.stdin.read().split()
n = int(data[0])
counts = Counter(map(int, data[1:1 + n]))
best = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
print(best[0])
""",
        tests=[
            T(stdin="6\n4 2 4 7 2 4\n", visible=True),
            T(stdin="4\n5 9 9 5\n", probe="edge:duplicates"),
            T(stdin="3\n8 8 8\n", probe="edge:all-equal"),
        ],
    ),
    # ---------------- L7 (easy-medium, two-pointers) ----------------
    Q(
        qid="L07-A",
        level=7,
        topic="two-pointers",
        title="Sorted Pact",
        prompt="""
The treaty scroll lists tribute values in NON-DECREASING order. Two clans must
jointly pay exactly the demanded amount. Can two different entries do it?

Input: line 1: n and demand (2 <= n <= 10^5). Line 2: n integers in non-decreasing
order, |v| <= 10^9.
Output: YES or NO.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n, demand = int(data[0]), int(data[1])
vals = list(map(int, data[2:2 + n]))
i, j = 0, n - 1
ok = False
while i < j:
    s = vals[i] + vals[j]
    if s == demand:
        ok = True
        break
    if s < demand:
        i += 1
    else:
        j -= 1
print("YES" if ok else "NO")
""",
        tests=[
            T(stdin="5 11\n1 3 4 7 9\n", visible=True),
            T(stdin="4 3\n5 6 7 8\n", probe="edge:no-solution"),
            T(stdin="4 -6\n-5 -1 0 2\n", probe="edge:negative"),
        ],
    ),
    Q(
        qid="L07-B",
        level=7,
        topic="two-pointers",
        title="Compress the March",
        prompt="""
The marching column is sorted by banner number, but many soldiers carry the same
banner. How many DISTINCT banners pass the reviewing stand?

Input: line 1: n (1 <= n <= 10^5). Line 2: n integers in non-decreasing order.
Output: one integer - the count of distinct values.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
vals = data[1:1 + n]
count = 1
for i in range(1, n):
    if vals[i] != vals[i - 1]:
        count += 1
print(count)
""",
        tests=[
            T(stdin="7\n1 1 2 3 3 3 9\n", visible=True),
            T(stdin="4\n6 6 6 6\n", probe="edge:all-equal"),
            T(stdin="1\n5\n", probe="edge:single"),
        ],
    ),
    # ---------------- L8 (easy-medium, strings) ----------------
    Q(
        qid="L08-A",
        level=8,
        topic="strings",
        title="Anagram Seals",
        prompt="""
Two wax seals guard the archive door. They match if one seal's letters can be
rearranged into the other's - same letters, same counts.

Input: two lines, each 1..10^5 lowercase letters.
Output: YES if they are anagrams, else NO.
""",
        solution=r"""
import sys
from collections import Counter
a, b = sys.stdin.read().split()
print("YES" if Counter(a) == Counter(b) else "NO")
""",
        tests=[
            T(stdin="listen\nsilent\n", visible=True),
            T(stdin="torch\ntorche\n", probe="edge:unbalanced"),
            T(stdin="aabbb\naaabb\n", probe="edge:duplicates"),
        ],
    ),
    Q(
        qid="L08-B",
        level=8,
        topic="strings",
        title="Caesar's Torch",
        prompt="""
The wall text was enciphered by shifting every letter FORWARD k places in the
alphabet (wrapping z -> a). Undo the shift and reveal the message.

Input: line 1: k (0 <= k <= 10^9). Line 2: 1..10^5 lowercase letters (ciphertext).
Output: the deciphered message.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
k = int(data[0]) % 26
s = data[1]
print("".join(chr((ord(c) - 97 - k) % 26 + 97) for c in s))
""",
        tests=[
            T(stdin="3\ngxqjhrq\n", visible=True),
            T(stdin="1\nabc\n", probe="edge:overflow"),
            T(stdin="52\nrecall\n", probe="edge:zero"),
        ],
    ),
    # ---------------- L9 (easy-medium, arrays) ----------------
    Q(
        qid="L09-A",
        level=9,
        topic="arrays",
        title="Ledger of Halls",
        prompt="""
The steward's ledger lists the gold stored in halls 1..n. Answer q audits: each
asks for the total gold in halls l through r inclusive.

Input: line 1: n and q (1 <= n, q <= 10^5). Line 2: n integers (|v| <= 10^6).
Then q lines, each "l r" with 1 <= l <= r <= n.
Output: q lines - the requested sums. (Hint: precompute prefix sums.)
""",
        solution=r"""
import sys
data = sys.stdin.buffer.read().split()
n, q = int(data[0]), int(data[1])
vals = list(map(int, data[2:2 + n]))
prefix = [0]
for v in vals:
    prefix.append(prefix[-1] + v)
out = []
idx = 2 + n
for _ in range(q):
    l, r = int(data[idx]), int(data[idx + 1])
    idx += 2
    out.append(str(prefix[r] - prefix[l - 1]))
print("\n".join(out))
""",
        tests=[
            T(stdin="5 3\n1 2 3 4 5\n1 3\n2 4\n5 5\n", visible=True),
            T(stdin="4 1\n-2 8 -1 3\n1 4\n", probe="edge:max-bounds"),
            T(stdin="3 2\n7 -7 7\n2 2\n1 1\n", probe="edge:single"),
        ],
    ),
    Q(
        qid="L09-B",
        level=9,
        topic="arrays",
        title="Balance Stone",
        prompt="""
A balance stone is a position where the total weight to its LEFT equals the total
weight to its RIGHT (either side may be empty, counting as 0). Find the first one.

Input: line 1: n (1 <= n <= 10^5). Line 2: n integers, |v| <= 10^6.
Output: the smallest 1-based index that balances, or -1 if none.
""",
        solution=r"""
import sys
data = sys.stdin.read().split()
n = int(data[0])
vals = list(map(int, data[1:1 + n]))
total = sum(vals)
left = 0
ans = -1
for i, v in enumerate(vals):
    if left == total - left - v:
        ans = i + 1
        break
    left += v
print(ans)
""",
        tests=[
            T(stdin="6\n2 3 4 1 4 4\n", visible=True),
            T(stdin="4\n1 2 3 4\n", probe="edge:no-solution"),
            T(stdin="3\n5 0 -5\n", probe="edge:empty"),
        ],
    ),
    # ---------------- L10 BOSS (medium, sliding-window) ----------------
    Q(
        qid="L10-B1",
        level=10,
        topic="sliding-window",
        title="Warden of Repetition",
        is_boss=True,
        time_limit_s=4,
        prompt="""
BOSS. The Warden lets you walk the gallery only while every rune underfoot is
distinct; step on a repeat and the floor resets. What is the longest stretch of
consecutive runes with no repeated character?

Input: one line of 1..10^5 lowercase letters.
Output: one integer - the length of the longest substring without repeating
characters.
""",
        solution=r"""
import sys
s = sys.stdin.read().strip()
last = {}
best = 0
start = 0
for i, c in enumerate(s):
    if c in last and last[c] >= start:
        start = last[c] + 1
    last[c] = i
    best = max(best, i - start + 1)
print(best)
""",
        tests=[
            T(stdin="abcabcbb\n", visible=True),
            T(stdin="bbbbbb\n", probe="edge:all-equal"),
            T(stdin="abcdefghijklmnopqrstuvwxyz\n", probe="edge:max-bounds"),
            T(gen=gen_word(100000), probe="perf:large_n"),
        ],
    ),
]

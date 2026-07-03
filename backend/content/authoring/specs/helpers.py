"""Small input-builder helpers shared by the spec modules."""

from __future__ import annotations

import random
import string


def rand_ints(rng: random.Random, n: int, lo: int, hi: int) -> list[int]:
    return [rng.randint(lo, hi) for _ in range(n)]


def arr_case(values: list[int], header_extra: str = "") -> str:
    """Standard "n[ extra]\\nv1 v2 ...\\n" stdin block."""
    head = f"{len(values)}{(' ' + header_extra) if header_extra else ''}"
    return f"{head}\n{' '.join(map(str, values))}\n"


def gen_arr(n: int, lo: int, hi: int, header_extra: str = ""):
    def gen(rng: random.Random) -> str:
        return arr_case(rand_ints(rng, n, lo, hi), header_extra)

    return gen


def rand_word(rng: random.Random, n: int, alphabet: str = string.ascii_lowercase) -> str:
    return "".join(rng.choice(alphabet) for _ in range(n))


def gen_word(n: int, alphabet: str = string.ascii_lowercase):
    def gen(rng: random.Random) -> str:
        return rand_word(rng, n, alphabet) + "\n"

    return gen


def edge_list(rng: random.Random, n: int, m: int, weighted: tuple[int, int] | None = None) -> list[str]:
    """m random (possibly duplicate) undirected/directed edge lines over nodes 1..n."""
    lines = []
    for _ in range(m):
        u = rng.randint(1, n)
        v = rng.randint(1, n)
        if weighted:
            lines.append(f"{u} {v} {rng.randint(*weighted)}")
        else:
            lines.append(f"{u} {v}")
    return lines

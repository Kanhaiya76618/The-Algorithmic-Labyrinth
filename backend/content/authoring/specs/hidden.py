"""Hidden dungeon: 10 short-answer logic/math puzzles, boss-tier, scaling 1->10.

No code execution - answers are compared as trimmed strings. Each prompt states
its answer format explicitly.
"""

from model import Puzzle

HIDDEN = [
    Puzzle(
        qid="H01",
        level=1,
        topic="math",
        title="The Glowing Rune",
        prompt="""
A rune glows with the LAST DIGIT of 7^2025. The powers of seven repeat their
final digits in a short cycle; find where 2025 lands.

Answer format: a single digit.
""",
        answer="7",
    ),
    Puzzle(
        qid="H02",
        level=2,
        topic="logic-puzzle",
        title="The Hundred Doors",
        prompt="""
100 doors stand closed. Spirit k (for k = 1..100) toggles every k-th door.
After all hundred spirits pass, how many doors stand open?

Answer format: a single integer.
""",
        answer="10",
    ),
    Puzzle(
        qid="H03",
        level=3,
        topic="math",
        title="Bones of Chance",
        prompt="""
Two fair six-sided bone dice clatter across the altar. What is the probability
their sum is exactly 8?

Answer format: a fraction in lowest terms, like 1/6.
""",
        answer="5/36",
    ),
    Puzzle(
        qid="H04",
        level=4,
        topic="math",
        title="The Factorial Vault",
        prompt="""
The vault's combination is the number of trailing zeros of 100! (one hundred
factorial). Count the tens hiding in the product.

Answer format: a single integer.
""",
        answer="24",
    ),
    Puzzle(
        qid="H05",
        level=5,
        topic="logic-puzzle",
        title="The Rotten Bridge",
        prompt="""
Four adventurers must cross a rotten bridge at night. It holds two at a time,
and the party's one torch must accompany every crossing. Crossing times: 1, 2,
5 and 10 minutes; a pair moves at the slower one's pace. What is the minimum
total time for all four to cross?

Answer format: a single integer (minutes).
""",
        answer="17",
    ),
    Puzzle(
        qid="H06",
        level=6,
        topic="math",
        title="The Three Chests",
        prompt="""
Three chests: one holds the key, two hold vipers. You pick one. The dungeon
keeper - who knows the contents - opens one of the OTHER chests, always
revealing a viper, and offers you the chance to switch. What is the probability
of finding the key if you always switch?

Answer format: a fraction in lowest terms.
""",
        answer="2/3",
    ),
    Puzzle(
        qid="H07",
        level=7,
        topic="math",
        title="Two Heads of the Hydra",
        prompt="""
You flip a fair coin until it shows heads twice IN A ROW. What is the expected
total number of flips?

Answer format: a single integer.
""",
        answer="6",
    ),
    Puzzle(
        qid="H08",
        level=8,
        topic="logic-puzzle",
        title="The Poisoned Cask",
        prompt="""
Exactly one of 1000 casks is poisoned. A single sip kills a taster overnight -
tonight is the only night, and the feast is at dawn. Tasters may sip from any
number of casks. What is the minimum number of tasters that GUARANTEES
identifying the poisoned cask by morning?

Answer format: a single integer.
""",
        answer="10",
    ),
    Puzzle(
        qid="H09",
        level=9,
        topic="math",
        title="The Circle of Forty-One",
        prompt="""
41 cultists stand in a circle, numbered 1 to 41. Counting starts at cultist 1;
every THIRD cultist still standing is banished (so 3, 6, 9, ... fall first).
The counting continues around the shrinking circle until one remains. Which
position survives?

Answer format: a single integer (the surviving position).
""",
        answer="31",
    ),
    Puzzle(
        qid="H10",
        level=10,
        topic="logic-puzzle",
        title="The Camel's Ledger",
        prompt="""
A merchant has 3000 enchanted bananas and a camel that carries at most 1000 at
a time. The market lies 1000 leagues away, and the camel eats 1 banana per
league walked (in either direction). Bananas may be cached anywhere along the
road, and distances need not be whole leagues. What is the greatest WHOLE
number of bananas that can reach the market?

Answer format: a single integer.
""",
        answer="533",
    ),
]

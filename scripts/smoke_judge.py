"""Piston judge smoke: one real submission per supported language.

Prereqs: docker compose up -d piston + the one-time package install
(backend/judge/README.md). Run:  python3 scripts/smoke_judge.py

Each submission reads two ints from stdin and prints their sum; the second
test carries a probe label and expects the WRONG output, so the harness also
proves failed-probe collection end to end.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.judge.client import run_submission  # noqa: E402

TESTS = [
    {"stdin": "2 3\n", "expected_stdout": "5", "probe": None, "visible": True},
    # deliberately wrong expectation — must fail and surface its probe label
    {"stdin": "10 20\n", "expected_stdout": "31", "probe": "edge:probe-check", "visible": False},
]

SUBMISSIONS = {
    "python3": "print(sum(map(int, input().split())))",
    "java": (
        "import java.util.*;\n"
        "public class Main { public static void main(String[] a) {\n"
        "  Scanner s = new Scanner(System.in);\n"
        "  System.out.println(s.nextInt() + s.nextInt()); } }"
    ),
    "c++": (
        "#include <iostream>\n"
        "int main() { long a, b; std::cin >> a >> b; std::cout << a + b; return 0; }"
    ),
    "c": (
        "#include <stdio.h>\n"
        "int main() { long a, b; scanf(\"%ld %ld\", &a, &b); printf(\"%ld\", a + b); return 0; }"
    ),
}


async def main() -> int:
    failed = []
    for lang, code in SUBMISSIONS.items():
        verdict = await run_submission(code, lang, TESTS, time_limit_s=3)
        ok = (
            verdict["verdict"] == "wrong_answer"  # test 2 is a planted failure
            and verdict["tests_passed"] == 1
            and verdict["tests_total"] == 2
            and verdict["failed_probes"] == ["edge:probe-check"]
        )
        if verdict["verdict"] == "judge_offline":
            print(f"[FAIL] {lang}: judge_offline — is Piston up with runtimes installed?")
            failed.append(lang)
            continue
        print(f"[{'PASS' if ok else 'FAIL'}] {lang}: verdict={verdict['verdict']} "
              f"{verdict['tests_passed']}/{verdict['tests_total']} "
              f"probes={verdict['failed_probes']} runtime={verdict['runtime_ms']}ms")
        if not ok:
            failed.append(lang)
    print("\n" + ("JUDGE SMOKE PASSED (4/4 languages)" if not failed
                  else f"JUDGE SMOKE FAILED: {failed}"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

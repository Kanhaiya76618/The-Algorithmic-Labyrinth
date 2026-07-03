# Judge — self-hosted Piston

Real code execution via [Piston](https://github.com/engineer-man/piston)
(open-source engine), run as a Docker service. Not a paid API, not a hand-rolled
sandbox.

## Start the engine

```bash
docker compose up -d piston
```

The API binds to `127.0.0.1:2000` — reachable by the backend on this host,
invisible to the network.

## One-time runtime install (Piston ships EMPTY)

```bash
# python3
curl -s -XPOST http://127.0.0.1:2000/api/v2/packages -H 'Content-Type: application/json' -d '{"language":"python","version":"3.10.0"}'
# java
curl -s -XPOST http://127.0.0.1:2000/api/v2/packages -H 'Content-Type: application/json' -d '{"language":"java","version":"15.0.2"}'
# c and c++ (one gcc package provides both)
curl -s -XPOST http://127.0.0.1:2000/api/v2/packages -H 'Content-Type: application/json' -d '{"language":"gcc","version":"10.2.0"}'
# verify
curl -s http://127.0.0.1:2000/api/v2/runtimes
```

Packages persist in the `piston_packages` volume; install once per machine.

## Supported languages (exactly these four)

| Game id | Piston language | Toolchain |
|---|---|---|
| `python3` | `python` | CPython 3.10 |
| `java` | `java` | OpenJDK 15 (class must be `Main`) |
| `c++` | `c++` | g++ 10.2 |
| `c` | `c` | gcc 10.2 |

## Resource limits

- Per-test wall clock: the question's `time_limit_s` + a language grace
  (python 0.5s, java 2s, c/c++ 0.3s) — java pays a JVM startup tax.
- Compile timeout: 15s.
- Memory: Piston's runtime defaults; question `memory_limit_mb` is advisory.
- Every test case is executed (no fail-fast after the first wrong answer) so
  ALL failed probe labels are collected — that's the memory signal.

## Verdicts

`accepted | wrong_answer | timeout | compile_error | runtime_error |
judge_offline`. `judge_offline` means Piston was unreachable — the game loop
must treat it as "no judgement", never as a player failure, and never crash.

## Smoke test (5 lines)

```python
import asyncio
from backend.judge.client import run_submission
tests = [{"stdin": "2 3\n", "expected_stdout": "5", "probe": None}]
verdict = asyncio.run(run_submission("print(sum(map(int, input().split())))", "python3", tests, 2))
print(verdict)  # expect: passed=True, verdict='accepted', 1/1
```

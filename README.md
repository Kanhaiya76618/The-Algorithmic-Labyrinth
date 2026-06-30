# Dungeon of Recall — Team Scaffold

A 4-person scaffold designed so everyone works in parallel **without merge
conflicts**. The whole design rests on one rule:

> **One file = one owner. Everyone codes against frozen contracts, never
> against each other's code.**

---

## Ownership map

| Path | Owner | Touches |
|------|-------|---------|
| `contracts/` | **Role A (lead)** | ⚠️ FROZEN — change only in a team huddle |
| `backend/main.py`, `deps.py`, `config.py` | **Role A** | set up once, then frozen |
| `backend/memory/`, `backend/stubs/` | **Role A** | Cognee + feedback loop |
| `backend/game/` | **Role B** | engine, progression, policy |
| `backend/content/` + `data/*.json` | **Role C** | questions (DATA, not code) |
| `frontend/` | **Role D** | UI, memory view, demo |
| `frontend/src/main.jsx`, `App.jsx` | A + D | routes wired once, then frozen |

`/.github/CODEOWNERS` enforces this automatically — GitHub requests the
correct reviewer for every path.

---

## Why this avoids merge conflicts

1. **Frozen seams.** The only files multiple people depend on are
   `contracts/schemas.py` and `contracts/memory_interface.py`. They are
   written Day 1 and changed only in a 5-minute huddle. Everyone imports
   from them; nobody redefines shapes locally.
2. **Interface + stub.** Roles B/C/D build against `MemoryService`
   (abstract) and run with `FakeMemoryService` (canned data). They never
   wait for Role A and never edit Role A's files. When the real Cognee
   service is ready, it's a **one-line env flip** (`MEMORY_BACKEND=cognee`).
3. **Aggregators written once.** `backend/main.py` and `frontend/main.jsx`
   include all routers/routes on Day 1 against stubs that already exist, so
   the "everyone adds their route to the big file" conflict never happens.
4. **Questions are DATA.** Role C edits JSON in `content/data/`, not code.
   Separate files, append-only — trivial to merge.
5. **Per-feature files.** No shared god-component. Each page/component is
   its own file.

---

## Git workflow

```
main (protected)  ←  dev  ←  feat/memory | feat/game | feat/content | feat/ui
```

- One long-lived branch per role: `feat/memory`, `feat/game`, `feat/content`, `feat/ui`.
- **Every morning:** `git pull --rebase origin dev` before you start.
- Small PRs into `dev`, merged often. Never commit to `main` directly.
- Never edit another role's directory without a heads-up in chat.
- Changing a `contracts/` file = announce it, change it ONCE, let the type
  checker show everyone what to fix in their own slice.

---

## Run it (works on Day 1 with zero Cognee setup)

```bash
# backend  — runs on the stub out of the box (MEMORY_BACKEND=fake)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit later; fake backend needs no keys
uvicorn backend.main:app --reload      # http://localhost:8000/docs

# frontend
cd frontend && npm install && npm run dev   # http://localhost:5173
```

Role A flips `MEMORY_BACKEND=cognee` once `backend/memory/service.py` is
wired — nothing else in the codebase changes.

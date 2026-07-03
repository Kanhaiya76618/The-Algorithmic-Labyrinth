"""Central env loading. Import this before anything that reads os.environ
(cognee reads LLM_*, DB_*, CACHING, ENABLE_BACKEND_ACCESS_CONTROL directly
from the environment via pydantic-settings).
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

MEMORY_BACKEND = os.environ.get("MEMORY_BACKEND", "fake").lower()

# Project-local storage for cognee's data/system roots + our episode journal.
# NEVER the default (inside site-packages — wiped on reinstall).
COGNEE_DATA_ROOT = Path(os.environ.get("COGNEE_DATA_ROOT", REPO_ROOT / "data" / "cognee")).resolve()

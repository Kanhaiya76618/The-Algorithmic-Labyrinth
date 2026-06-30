"""Role A — settings. Reads .env. No secrets committed."""
from __future__ import annotations
import os


class Settings:
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    # Flip to "fake" so the rest of the team can run with zero Cognee setup.
    # Role A flips to "cognee" once backend/memory/service.py is ready.
    MEMORY_BACKEND = os.getenv("MEMORY_BACKEND", "fake")   # "fake" | "cognee"
    COGNEE_SERVICE_URL = os.getenv("COGNEE_SERVICE_URL", "")
    COGNEE_API_KEY = os.getenv("COGNEE_API_KEY", "")


settings = Settings()

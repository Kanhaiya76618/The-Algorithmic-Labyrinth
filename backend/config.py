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

# OpenAI-compatible gateways (e.g. AI/ML API, aimlapi.com) validate the
# embeddings `encoding_format` field strictly and reject the `null` that
# litellm emits by default ("Expected 'float' | 'base64', received null"),
# even though real OpenAI tolerates it. When a custom EMBEDDING_ENDPOINT is
# configured we default it to "float" (OpenAI's own default, so this is a
# no-op for the real OpenAI path). Applied here because cognee's
# LiteLLMEmbeddingEngine builds the embedding call without this param and
# exposes no passthrough for it.
if os.environ.get("EMBEDDING_ENDPOINT"):
    try:
        import litellm

        def _force_encoding_format(fn):
            def wrapper(*args, **kwargs):
                if kwargs.get("encoding_format") is None:
                    kwargs["encoding_format"] = "float"
                return fn(*args, **kwargs)

            return wrapper

        litellm.aembedding = _force_encoding_format(litellm.aembedding)
        litellm.embedding = _force_encoding_format(litellm.embedding)
    except Exception:  # litellm import failures must not break keyless/fake dev
        pass

# Project-local storage for cognee's data/system roots + our episode journal.
# NEVER the default (inside site-packages — wiped on reinstall).
COGNEE_DATA_ROOT = Path(os.environ.get("COGNEE_DATA_ROOT", REPO_ROOT / "data" / "cognee")).resolve()

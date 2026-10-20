import os

import streamlit as st

MODEL_ID = "claude-haiku-5-5"

APP_TITLE = "Club Council"
APP_TAGLINE = "Rooms of expert agents that deliberate, grounded in live search."


def _secret(key: str) -> str:
    try:
        value = st.secrets.get(key, "")
    except Exception:
        value = ""
    return value or os.getenv(key, "")


SERPAPI_API_KEY = _secret("SERPAPI_API_KEY")
ANTHROPIC_API_KEY = _secret("ANTHROPIC_API_KEY")


def missing_keys() -> list[str]:
    missing = []
    if not SERPAPI_API_KEY:
        missing.append("SERPAPI_API_KEY")
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    return missing

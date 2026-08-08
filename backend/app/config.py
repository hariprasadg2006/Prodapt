"""
Configuration module — loads environment variables and validates required keys.
"""

import os
from dotenv import load_dotenv

# Load .env file from the backend directory
load_dotenv()

OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")


def validate_config() -> None:
    """Fail fast if required environment variables are missing."""
    if not OPENROUTER_API_KEY and not GEMINI_API_KEY:
        raise RuntimeError(
            "Neither OPENROUTER_API_KEY nor GEMINI_API_KEY environment variable is set. "
            "Add OPENROUTER_API_KEY or GEMINI_API_KEY to your .env file."
        )


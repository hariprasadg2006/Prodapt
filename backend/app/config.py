"""
Configuration module — loads environment variables and validates required keys.
"""

import os
from dotenv import load_dotenv

# Load .env file from the backend directory
load_dotenv()

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")


def validate_config() -> None:
    """Fail fast if required environment variables are missing."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set. "
            "Copy .env.example to .env and add your key."
        )

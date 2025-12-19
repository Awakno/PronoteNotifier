"""Basic health check for PronoteNotifier configuration.

This script validates presence of required environment variables and that
all key modules can be imported without triggering network calls.
Run with: python scripts/health_check.py
"""

import sys
from pathlib import Path
from utils.env import get_env_variable

REQUIRED_KEYS = [
    "PRONOTE_URL",
    "PRONOTE_USERNAME",
    "PRONOTE_PASSWORD",
]
OPTIONAL_KEYS = [
    "DISCORD_WEBHOOK_URL",
    "CUSTOM_WEBHOOK_URL",
    "CUSTOM_WEBHOOK_PASS",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "DEBUG",
]


def main():
    env = get_env_variable()
    missing = [k for k in REQUIRED_KEYS if not env.get(k)]

    print("Detected .env file:", Path(".env").exists())
    if missing:
        print("Missing required keys:", ", ".join(missing))
        sys.exit(1)

    print("All required keys present.")
    # Echo optional keys state for visibility
    for key in OPTIONAL_KEYS:
        val = env.get(key)
        print(f"{key}: {'set' if val else 'not set'}")

    # Import webhook providers to ensure no ImportError
    try:
        import webhook.telegram  # noqa: F401
    except Exception as exc:  # pragma: no cover
        print(f"Telegram provider import failed: {exc}")
        sys.exit(1)

    print("Health check completed successfully.")


if __name__ == "__main__":
    main()

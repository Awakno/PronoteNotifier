"""utils.env
Helpers to read environment variables from a .env file with sensible
fallback to the process environment. Parsing is defensive.
"""

import os
from typing import Dict


def get_env_variable() -> Dict[str, str]:
    data: Dict[str, str] = {}
    try:
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                data[key.strip()] = value.strip().strip('"').strip("'")
    except FileNotFoundError:
        # No .env file present — fall back to environment variables
        pass

    # Overlay any missing values with actual environment variables
    for k, v in os.environ.items():
        if k not in data:
            data[k] = v

    return data

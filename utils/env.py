"""
This file is used to read the environment variables from the .env file.
"""

def get_env_variable():
    f = open(".env", "r")
    data = {}
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        key, value = line.strip().split("=")
        data[key] = value.replace('"', "")
    return data

from utils.env import get_env_variable

env = get_env_variable()


def debug_mode():
    return str(env.get("DEBUG", "False")).lower() in ("1", "true", "yes")

from utils.env import get_env_variable

env = get_env_variable()

def debug_mode():
    if env['DEBUG'] == "True":
        return True
    return False

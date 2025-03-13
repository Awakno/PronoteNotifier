import sys
import requests
import pronotepy
from utils.debug_mode import debug_mode
from utils.env import get_env_variable

env = get_env_variable()

SESSION = None


def initialize_session():
    global SESSION
    try:
        session = pronotepy.Client(
            pronote_url=env.get("PRONOTE_URL"),
            username=env.get("PRONOTE_USERNAME"),
            password=env.get("PRONOTE_PASSWORD"),
            uuid="PronoteNotifier",
        )
        if not session.logged_in:
            print(
                "Erreur : Impossible de se connecter à Pronote. Vérifiez vos identifiants."
            )
            sys.exit(1)
        SESSION = session
        return session
    except Exception as e:
        print(f"Erreur lors de la connexion à Pronote : {e}")
        if debug_mode():
            print("Traceback :")
            import traceback

            traceback.print_exc()
            requests.post(
                get_env_variable()["DISCORD_WEBHOOK_URL"],
                json={"content": f"Erreur lors de la connexion à Pronote : {e}"},
            )
        sys.exit(1)


def check_and_refresh_session():
    global SESSION
    try:
        if SESSION.session_check():
            print("Session rafraîchie.")
    except Exception as e:
        print(f"Erreur lors du rafraîchissement de la session : {e}")
        initialize_session()


SESSION = initialize_session()

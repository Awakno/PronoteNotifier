import sys
import pronotepy
from utils.env import get_env_variable

env = get_env_variable()

def initialize_session():  
    try:
        session = pronotepy.Client(
            pronote_url=env.get("PRONOTE_URL"),
            username=env.get("PRONOTE_USERNAME"),
            password=env.get("PRONOTE_PASSWORD"),
            uuid="PronoteNotifier",
        )
        if not session.logged_in:
            print("Erreur : Impossible de se connecter à Pronote. Vérifiez vos identifiants.")
            sys.exit(1)
        return session
    except Exception as e:
        print(f"Erreur lors de la connexion à Pronote : {e}")
        sys.exit(1)

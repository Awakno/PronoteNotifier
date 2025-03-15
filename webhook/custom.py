import requests
from message.Status import Debug, Error
from utils.env import get_env_variable
from utils.debug_mode import debug_mode

env = get_env_variable()


async def send_custom_webhook(data):
    """
    Envoie une notification personnalisée via un webhook.
    :param data: dict: Données à envoyer
    """
    custom_webhook_url = env.get("CUSTOM_WEBHOOK_URL")
    custom_webhook_pass = env.get("CUSTOM_WEBHOOK_PASS")

    if not custom_webhook_url or not custom_webhook_pass:
        if debug_mode():
            print(Debug("Aucune URL de webhook personnalisée définie."))
        return

    try:
        response = requests.post(
            custom_webhook_url,
            json={"metadata": {"pass": custom_webhook_pass}, "data": data},
        )
        if response.status_code != 200:
            print(Error(f"Erreur lors de l'envoi du webhook personnalisé : {response.status_code}"))
    except requests.RequestException as e:
        print(Error(f"Erreur réseau lors de l'envoi du webhook personnalisé : {e}"))
    except Exception as e:
        print(Error(f"Erreur inattendue lors de l'envoi du webhook personnalisé : {e}"))

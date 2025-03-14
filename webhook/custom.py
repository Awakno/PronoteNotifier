import requests
from message.Status import Error
from utils.env import get_env_variable
from utils.debug_mode import debug_mode
env = get_env_variable()


async def send_custom_webhook(data):
    """
    Envoie une notification personnalisée via un webhook
    :param data: dict: Données à envoyer
    """
    if not env.get("CUSTOM_WEBHOOK_URL") or not env.get("CUSTOM_WEBHOOK_PASS"):
        if debug_mode():
            print("[DEBUG]: Aucun webhook personnalisé n'a été défini.")
        return
    try:
        # Envoi de la notification personnalisée
        custom_webhook_url = env.get("CUSTOM_WEBHOOK_URL")
        custom_webhook_pass = env.get("CUSTOM_WEBHOOK_PASS")
        if custom_webhook_url and custom_webhook_pass:
            rq = requests.post(custom_webhook_url, json={"metadata": {"pass": custom_webhook_pass}, "data": data})
            if rq.status_code != 200:
                print(Error(f"Erreur lors de l'envoi du webhook personnalisé : {rq.status_code}"))
    except Exception as e:
        print(Error(f"Erreur lors de l'envoi du webhook personnalisé : {e}"))

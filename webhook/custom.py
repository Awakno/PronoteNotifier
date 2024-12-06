import requests
from utils.env import get_env_variable
from utils.debug_mode import debug_mode
env = get_env_variable()


async def send_custom_webhook(grade):
    if not env.get("CUSTOM_WEBHOOK_URL") or not env.get("CUSTOM_WEBHOOK_PASS"):
        if debug_mode():
            print("[DEBUG]: Aucun webhook personnalisé n'a été défini.")
        return
    try:
        # Envoi de la notification personnalisée
        custom_webhook_url = env.get("CUSTOM_WEBHOOK_URL")
        custom_webhook_pass = env.get("CUSTOM_WEBHOOK_PASS")
        if custom_webhook_url and custom_webhook_pass:
            rq = requests.post(custom_webhook_url, json={"metadata": {"pass": custom_webhook_pass}, "data": grade})
            if rq.status_code != 200:
                print(f"Erreur lors de l'envoi du webhook personnalisé : {rq.text}")
    except Exception as e:
        print(f"Erreur lors de l'envoi du webhook personnalisé : {e}")

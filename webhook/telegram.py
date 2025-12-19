import asyncio
import requests
from utils.env import get_env_variable
from utils.debug_mode import debug_mode

env = get_env_variable()

TELEGRAM_TOKEN = env.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = env.get("TELEGRAM_CHAT_ID")
TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


async def send_telegram_message(handler_type: str, data):
    """Send a formatted Telegram message depending on handler_type.

    This function runs the blocking HTTP call in a thread to avoid blocking
    the asyncio event loop.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        if debug_mode():
            print(
                "Telegram not configured: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing"
            )
        return

    text = ""
    try:
        if handler_type == "grade":
            # pronotepy.Grade
            text = (
                f"📢 <b>Nouvelle note</b>\n"
                f"<b>Matière:</b> {data.subject.name}\n"
                f"<b>Note:</b> {data.grade}/{getattr(data, 'out_of', '')}\n"
                f"<b>Date:</b> {data.date.strftime('%d/%m/%Y')}\n"
                f"<b>Commentaire:</b> {data.comment or 'Aucun'}"
            )
        elif handler_type == "homework":
            text = (
                f"📝 <b>Nouveau devoir</b>\n"
                f"<b>Matière:</b> {data.subject.name}\n"
                f"<b>Pour le:</b> {getattr(data, 'date', '')}\n"
                f"<b>Description:</b> {getattr(data, 'description', '')}"
            )
        elif handler_type in ("news", "discussion"):
            title = getattr(data, "title", getattr(data, "subject", "Actualité"))
            author = getattr(data, "author", getattr(data, "creator", ""))
            content = getattr(data, "content", None)
            if not content and getattr(data, "messages", None):
                try:
                    content = data.messages[-1].content
                except Exception:
                    content = ""
            text = (
                f"📰 <b>Nouvelle {handler_type}</b>\n"
                f"<b>Titre:</b> {title}\n"
                f"<b>Auteur:</b> {author}\n"
                f"<b>Contenu:</b> {content}"
            )
        elif handler_type == "edt":
            # lesson/hour object
            text = (
                f"📚 <b>Événement EDT</b>\n"
                f"<b>Matière:</b> {data.subject.name}\n"
                f"<b>Début:</b> {getattr(data, 'start', '')}\n"
                f"<b>Fin:</b> {getattr(data, 'end', '')}\n"
                f"<b>Statut:</b> {getattr(data, 'status', '')}\n"
                f"<b>Annulé:</b> {getattr(data, 'canceled', False)}"
            )
        else:
            text = f"Notification ({handler_type}): {str(data)}"
    except Exception as e:
        if debug_mode():
            print(f"Erreur lors du format Telegram: {e}")
        text = f"Notification ({handler_type})"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    def post():
        url = TELEGRAM_API.format(token=TELEGRAM_TOKEN)
        return requests.post(url, data=payload, timeout=10)

    try:
        response = await asyncio.to_thread(post)
        if response.status_code != 200 and debug_mode():
            print(f"Telegram send failed: {response.status_code} - {response.text}")
    except Exception as e:
        if debug_mode():
            print(f"Erreur Telegram: {e}")

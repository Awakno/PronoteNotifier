from discord_webhook import DiscordEmbed, DiscordWebhook
import pronotepy
from utils.env import get_env_variable
from utils.debug_mode import debug_mode

env = get_env_variable()
WEBHOOK = env.get("DISCORD_WEBHOOK_URL")


async def send_discord_news_webhook(news: pronotepy.Information):
    """
    Sends a Discord notification for a new news item.
    :param news: pronotepy.Information: News item to notify
    """
    if not WEBHOOK:
        if debug_mode():
            print("[DEBUG]: No Discord webhook URL defined.")
        return

    try:
        # Prepare the Discord webhook
        discord_webhook = DiscordWebhook(url=WEBHOOK)
        subject = news.content[:1000] if news.content else "Pas de commentaire disponible"
        embed = DiscordEmbed(
            title="📢 Nouvelle Actualité Reçue",
            description=f"**{news.title}**\n\n{subject}",
            color=0x3498DB,  # Blue color for a more vibrant look
        )
        embed.add_embed_field(name="✍️ Auteur", value=news.author or "Inconnu", inline=False)
        embed.add_embed_field(
            name="📅 Date", value=news.start_date.strftime("%d/%m/%Y"), inline=True
        )
        embed.set_footer(text="Pronote Notifier 🇫🇷")
        embed.set_timestamp()

        discord_webhook.add_embed(embed)
        discord_webhook.execute()
    except Exception as e:
        if debug_mode():
            print(f"[DEBUG]: Erreur lors de l'envoi du webhook Discord : {e}")

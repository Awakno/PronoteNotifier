from discord_webhook import DiscordEmbed, DiscordWebhook
import pronotepy
from utils.env import get_env_variable
from utils.debug_mode import debug_mode

env = get_env_variable()
WEBHOOK = env["DISCORD_WEBHOOK_URL"]

async def send_discord_news_webhook(news: pronotepy.Information):
    """
    Envoie une notification Discord pour une nouvelle actualité
    :param news: pronotepy.Information: Actualité à notifier
    """
    if not WEBHOOK:
        if debug_mode():
            print("[DEBUG]: Aucun webhook Discord n'a été défini.")
        return
    try:
        # Envoi de la notification Discord
        discord_webhook = DiscordWebhook(url=WEBHOOK)
        subject = news.content[:1000] if news.content else "Aucun commentaire"
        embed = DiscordEmbed(
            title="Nouvelle actualité reçue",
            description=f"**{news.title}**\n\n{subject}",
            color=242424,
        )
        embed.add_embed_field(name="Auteur", value=news.author, inline=False)
        embed.add_embed_field(
            name="Date", value=news.start_date.strftime("%d/%m/%Y"), inline=True
        )
        embed.set_footer(text="Pronote Notifier")
        embed.set_timestamp()
        discord_webhook.add_embed(embed)
        discord_webhook.execute()
    except Exception as e:
        if debug_mode():
            print(f"Erreur lors de l'envoi du webhook Discord : {e}")

from discord_webhook import DiscordEmbed, DiscordWebhook
import pronotepy
from utils.env import get_env_variable
from utils.debug_mode import debug_mode

env = get_env_variable()
WEBHOOK = env.get("DISCORD_WEBHOOK_URL")


async def send_discord_discussions_webhook(discussion: pronotepy.Discussion):
    """
    Sends a Discord notification for a new discussion.
    :param discussion: pronotepy.Discussion: Discussion to notify
    """
    if not WEBHOOK:
        if debug_mode():
            print("[DEBUG]: Aucune URL de webhook Discord définie. ❌")
        return

    if not discussion:
        if debug_mode():
            print("[DEBUG]: Aucune discussion fournie. ❌")
        return

    try:
        # Préparer le webhook Discord
        discord_webhook = DiscordWebhook(url=WEBHOOK)
        sujet = (
            discussion.messages[-1].content[:1000]
            if discussion.messages
            else "Pas de commentaires 📝"
        )
        embed = DiscordEmbed(
            title="🆕 Nouvelle Discussion Créée",
            description=f"**{discussion.subject}**\n\n{sujet}",
            color=0x3498DB,  # Hexadécimal pour une meilleure lisibilité
        )
        embed.add_embed_field(name="👤 Auteur", value=discussion.creator, inline=False)
        embed.add_embed_field(
            name="📅 Date",
            value=discussion.date.strftime("%d/%m/%Y %H:%M:%S"),
            inline=True,
        )
        embed.set_footer(text="Pronote Notifier 🚀")
        embed.set_timestamp()

        # Envoyer le webhook
        discord_webhook.add_embed(embed)
        discord_webhook.execute()
    except Exception as e:
        if debug_mode():
            print(f"[DEBUG]: Erreur lors de l'envoi du webhook Discord : {e} ❗")

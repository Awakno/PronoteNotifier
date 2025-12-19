from discord_webhook import DiscordEmbed, DiscordWebhook
import pronotepy
import asyncio
from message.Status import Debug
from utils.env import get_env_variable
from utils.debug_mode import debug_mode

env = get_env_variable()
WEBHOOK = env.get("DISCORD_WEBHOOK_URL")


async def send_discord_grades_webhook(grade: pronotepy.Grade):
    """
    Sends a Discord notification for a new grade.
    :param grade: pronotepy.Grade: Grade to notify
    """
    if not WEBHOOK:
        if debug_mode():
            print(Debug("Aucune URL de webhook Discord définie."))
        return

    try:
        # Prepare Discord webhook and embed
        discord_webhook = DiscordWebhook(url=WEBHOOK)
        embed = DiscordEmbed(
            title="📢 Nouvelle Note Reçue 🎉",
            description=f"**📚 Matière :** {grade.subject.name}\n**✏️ Note :** {grade.grade}/{grade.out_of}",
            color=0x3498DB,
        )
        embed.add_embed_field(
            name="💬 Commentaire",
            value=grade.comment or "Aucun commentaire",
            inline=False,
        )
        embed.add_embed_field(
            name="📅 Date", value=grade.date.strftime("%d/%m/%Y"), inline=True
        )
        embed.set_footer(text="Pronote Notifier")
        embed.set_timestamp()

        # Execute webhook in a thread to avoid blocking
        def exec_webhook():
            discord_webhook.add_embed(embed)
            discord_webhook.execute()

        await asyncio.to_thread(exec_webhook)

    except Exception as e:
        if debug_mode():
            print(Debug(f"Erreur lors de l'envoi du webhook Discord : {e}"))

from discord_webhook import DiscordEmbed, DiscordWebhook
import pronotepy

from message.Status import Debug
from utils.debug_mode import debug_mode
from utils.env import get_env_variable

webhook = get_env_variable().get("DISCORD_WEBHOOK_URL")


async def send_discord_homeworks_webhook(homeworks: pronotepy.Homework):
    """
    Vérifie et notifie les nouveaux devoirs.
    """

    if not webhook:
        if debug_mode():
            print(Debug("Aucune URL de webhook Discord définie."))
        return

    wb = DiscordWebhook(url=webhook)
    embed = DiscordEmbed(
        title="📚 Nouveau devoir", description=homeworks.description, color=0x3498DB
    )
    embed.add_embed_field(
        name="📖 Matière", value=homeworks.subject.name or "Non spécifié", inline=False
    )
    embed.add_embed_field(
        name="📅Pour le", value=homeworks.date.strftime("%d/%m/%Y"), inline=True
    )
    embed.set_timestamp()
    wb.add_embed(embed)
    wb.execute()

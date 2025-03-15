from discord_webhook import DiscordEmbed, DiscordWebhook
import pronotepy
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
            print("[DEBUG]: No Discord webhook URL defined.")
        return

    try:
        # Prepare Discord webhook and embed
        discord_webhook = DiscordWebhook(url=WEBHOOK)
        embed = DiscordEmbed(
            title="New Grade Received",
            description=f"**Subject:** {grade.subject.name}\n**Grade:** {grade.grade}/{grade.out_of}",
            color=242424,
        )
        embed.add_embed_field(
            name="Comment", value=grade.comment or "No comment", inline=False
        )
        embed.add_embed_field(
            name="Date", value=grade.date.strftime("%d/%m/%Y"), inline=True
        )
        embed.set_footer(text="Pronote Notifier")
        embed.set_timestamp()

        # Add embed and execute webhook
        discord_webhook.add_embed(embed)
        discord_webhook.execute()

    except Exception as e:
        if debug_mode():
            print(f"[DEBUG]: Error sending Discord webhook: {e}")

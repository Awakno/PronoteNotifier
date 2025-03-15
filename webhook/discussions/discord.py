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
            print("[DEBUG]: No Discord webhook URL defined.")
        return

    if not discussion:
        if debug_mode():
            print("[DEBUG]: No discussion provided.")
        return

    try:
        # Prepare the Discord webhook
        discord_webhook = DiscordWebhook(url=WEBHOOK)
        subject = (
            discussion.messages[-1].content[:1000]
            if discussion.messages
            else "No comments"
        )
        embed = DiscordEmbed(
            title="New Discussion Created",
            description=f"**{discussion.subject}**\n\n{subject}",
            color=0x3A3A3A,  # Hexadecimal for better readability
        )
        embed.add_embed_field(name="Author", value=discussion.creator, inline=False)
        embed.add_embed_field(
            name="Date",
            value=discussion.date.strftime("%d/%m/%Y %H:%M:%S"),
            inline=True,
        )
        embed.set_footer(text="Pronote Notifier")
        embed.set_timestamp()

        # Send the webhook
        discord_webhook.add_embed(embed)
        discord_webhook.execute()
    except Exception as e:
        if debug_mode():
            print(f"[DEBUG]: Error sending Discord webhook: {e}")

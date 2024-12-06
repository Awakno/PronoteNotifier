from discord_webhook import DiscordEmbed, DiscordWebhook
from utils.env import get_env_variable
from utils.debug_mode import debug_mode

env = get_env_variable()
WEBHOOK = env["DISCORD_WEBHOOK_URL"]

async def send_discord_webhook(grade):
    if not WEBHOOK:
        if debug_mode():
            print("[DEBUG]: Aucun webhook Discord n'a été défini.")
        return
    try:
        # Envoi de la notification Discord
        discord_webhook = DiscordWebhook(url=WEBHOOK, content="@everyone")
        embed = DiscordEmbed(
            title=f"Nouvelle note : `{grade.subject.name}`",
            description=f"Sujet: **{grade.comment}** \nNote : **{grade.grade}**/{grade.out_of}",
            color=242424
        )
        embed.set_footer(text="Pronote Notifier")
        discord_webhook.add_embed(embed)
        discord_webhook.execute()
    except Exception as e:
        if debug_mode():
            print(f"Erreur lors de l'envoi du webhook Discord : {e}")

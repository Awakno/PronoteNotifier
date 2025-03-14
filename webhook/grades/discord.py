from discord_webhook import DiscordEmbed, DiscordWebhook
import pronotepy
from utils.env import get_env_variable
from utils.debug_mode import debug_mode

env = get_env_variable()
WEBHOOK = env["DISCORD_WEBHOOK_URL"]


async def send_discord_grades_webhook(grade: pronotepy.Grade):
    """
    Envoie une notification Discord pour une nouvelle actualité
    :param grade: pronotepy.Grade: Note à notifier
    """
    if not WEBHOOK:
        if debug_mode():
            print("[DEBUG]: Aucun webhook Discord n'a été défini.")
        return
    try:
        # Envoi de la notification Discord
        discord_webhook = DiscordWebhook(url=WEBHOOK)
        subject = f"**{grade.comment}**" if grade.comment else "Aucun commentaire"
        embed = DiscordEmbed(
            title="Nouvelle note reçue",
            description=f"**Matière :** {grade.subject.name}\n**Note :** {grade.grade}/{grade.out_of}",
            color=242424,
        )
        embed.add_embed_field(name="Commentaire", value=subject, inline=False)
        embed.add_embed_field(
            name="Date", value=grade.date.strftime("%d/%m/%Y"), inline=True
        )
        embed.set_footer(text="Pronote Notifier")
        embed.set_timestamp()
        discord_webhook.add_embed(embed)
        discord_webhook.execute()
    except Exception as e:
        if debug_mode():
            print(f"Erreur lors de l'envoi du webhook Discord : {e}")

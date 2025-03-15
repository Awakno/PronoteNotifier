from discord_webhook import DiscordEmbed, DiscordWebhook
import pronotepy
from utils.env import get_env_variable
from utils.debug_mode import debug_mode

WEBHOOK = get_env_variable().get("DISCORD_WEBHOOK_URL")


async def send_discord_edt_webhook(edt: pronotepy.Lesson):
    """
    Envoie une notification pour un nouvel événement dans l'emploi du temps.
    """
    if not WEBHOOK:
        if debug_mode():
            print("[DEBUG]: No Discord webhook URL defined.")
        return

    wb = DiscordWebhook(url=WEBHOOK)
    embed = DiscordEmbed(
        title="📚 Nouvel événement dans l'emploi du temps", color=0x3498DB
    )
    embed.add_embed_field(
        name="📖 Matière", value=edt.subject.name or "Non spécifié", inline=False
    )
    embed.add_embed_field(
        name="👩‍🏫 Professeurs",
        value=", ".join(edt.teacher_names) or "Non spécifié",
        inline=False,
    )
    embed.add_embed_field(
        name="🏫 Salle(s)",
        value=", ".join(str(classroom) for classroom in edt.classrooms)
        or "Non spécifié",
        inline=False,
    )
    embed.add_embed_field(
        name="📅 Date", value=edt.start.strftime("%d/%m/%Y"), inline=True
    )
    embed.add_embed_field(
        name="🕒 Heure",
        value=f"{edt.start.strftime('%H:%M')} - {edt.end.strftime('%H:%M')}",
        inline=True,
    )
    embed.add_embed_field(
        name="📌 Statut", value=edt.status if edt.status else "Normal", inline=True
    )
    embed.add_embed_field(
        name="❌ Annulé", value="Oui" if edt.canceled else "Non", inline=True
    )
    embed.add_embed_field(
        name="🔔 Durée",
        value=f"{(edt.end - edt.start).seconds // 60} minutes",
        inline=True,
    )
    embed.set_footer(text="Pronote Notifier")
    embed.set_timestamp()
    wb.add_embed(embed)
    wb.execute()

import sys
import pronotepy
import asyncio
from discord_webhook import DiscordWebhook, DiscordEmbed
from dotenv import load_dotenv
import os

load_dotenv()

# Variables globales
GRADES_CACHE = set()  # Utilisation d'un set pour suivre les notes déjà vues
WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

def initialize_session():
    try:
        session = pronotepy.Client(
            pronote_url=os.getenv("PRONOTE_URL"),
            username=os.getenv("PRONOTE_USERNAME"),
            password=os.getenv("PRONOTE_PASSWORD"),
            uuid="PronoteNotifier",
        )
        if not session.logged_in:
            print("Erreur : Impossible de se connecter à Pronote. Vérifiez vos identifiants.")
            sys.exit(1)
        return session
    except Exception as e:
        print(f"Erreur lors de la connexion à Pronote : {e}")
        sys.exit(1)

def initialize_grades_cache(session):
    """
    Initialise le cache avec toutes les notes existantes sans envoyer de notifications.
    """
    for period in session.periods:
        for grade in period.grades:
            # Ajout des notes sous forme d'une clé unique au cache
            grade_key = (period.name, grade.subject.name, grade.date.isoformat(), grade.grade)
            GRADES_CACHE.add(grade_key)

async def check_for_new_grades(session):
    """
    Vérifie périodiquement les nouvelles notes et envoie des notifications pour les ajouts.
    """
    while True:
        try:
            for period in session.periods:
                for grade in period.grades:
                    # Génération de la clé unique pour cette note
                    grade_key = (period.name, grade.subject.name, grade.date.isoformat(), grade.grade)
                    
                    if grade_key not in GRADES_CACHE:
                        # Nouvelle note détectée
                        GRADES_CACHE.add(grade_key)
                        print(f"Nouvelle note détectée : {grade.subject.name} - {grade.grade}")
                        await send_webhook(grade)
        except Exception as e:
            initialize_session()  # Reconnexion à Pronote en cas d'erreur
            print(f"Erreur pendant la vérification des notes : {e}")
        await asyncio.sleep(60)

async def send_webhook(grade):
    """
    Envoie une notification Discord pour une nouvelle note.
    """
    try:
        webhook = DiscordWebhook(url=WEBHOOK, content="@everyone")
        embed = DiscordEmbed(
            title=f"Nouvelle note : `{grade.subject.name}`",
            description=f"Sujet: **{grade.comment}** \nNote : **{grade.grade}**/{grade.out_of}",
            color=242424
        )
        embed.set_footer(text="Pronote Notifier")
        webhook.add_embed(embed)
        webhook.execute()
    except Exception as e:
        print(f"Erreur lors de l'envoi du webhook : {e}")

if __name__ == "__main__":
    session = initialize_session()
    initialize_grades_cache(session)  # Initialise le cache avec les notes existantes
    print("Initialisation terminée. Le programme surveille maintenant les nouvelles notes...")
    asyncio.run(check_for_new_grades(session))  # Boucle pour détecter les nouvelles notes

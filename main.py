import asyncio
from utils.debug_mode import debug_mode
from webhook.discord import send_discord_webhook
from api.session import initialize_session
from api.cache.grades import GRADES_CACHE, initialize_grades_cache

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
                        if debug_mode():
                            print(f"Nouvelle note détectée : {grade.subject.name} - {grade.grade}")
                        await handler_webhook(grade)
        except Exception as e:
            initialize_session()  # Reconnexion à Pronote en cas d'erreur
            print(f"Erreur pendant la vérification des notes : {e}")
        await asyncio.sleep(60)

async def handler_webhook(grade):
    """
    Envoie des notifications pour une nouvelle note à plusieurs webhooks.
    """
    await send_discord_webhook(grade)

if __name__ == "__main__":
    session = initialize_session()
    initialize_grades_cache(session)
    print("Initialisation terminée. Le programme surveille maintenant les nouvelles notes...")

    asyncio.run(check_for_new_grades(session))

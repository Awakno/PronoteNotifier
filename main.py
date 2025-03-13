from utils.debug_mode import debug_mode
from webhook.custom import send_custom_webhook
from webhook.discord import send_discord_webhook
from api.session import initialize_session, check_and_refresh_session
from api.cache.grades import GRADES_CACHE
import asyncio
from api.cache.handler import setup_cache_handler
from api.session import SESSION as session


async def check_for_new_grades(session):
    """
    Vérifie périodiquement les nouvelles notes et envoie des notifications pour les ajouts.
    """
    while True:
        try:
            check_and_refresh_session()  # Vérification et rafraîchissement de la session
            for period in session.periods:
                for grade in period.grades:
                    # Génération de la clé unique pour cette note
                    grade_key = (
                        period.name,
                        grade.subject.name,
                        grade.date.isoformat(),
                        grade.grade,
                    )
                    if grade_key not in GRADES_CACHE:
                        # Nouvelle note détectée
                        GRADES_CACHE.add(grade_key)
                        if debug_mode():
                            print(
                                f"Nouvelle note détectée : {grade.subject.name} - {grade.grade}"
                            )
                        await handler_webhook(grade)
        except Exception as e:
            initialize_session()  # Reconnexion à Pronote en cas d'erreur
            print(f"Erreur pendant la vérification des notes : {e}")
        await asyncio.sleep(60)


async def handler_webhook(grade):
    """
    Envoie des notifications pour une nouvelle note à plusieurs webhooks.
    """
    asyncio.gather(send_custom_webhook(grade), send_discord_webhook(grade))


if __name__ == "__main__":
    asyncio.run(setup_cache_handler())
    print(
        "Initialisation terminée. Le programme surveille maintenant les nouvelles notes..."
    )
    try:
        asyncio.run(check_for_new_grades(session))
    except KeyboardInterrupt:
        print("Arrêt du programme.")
        input("Appuyez sur une touche pour quitter...")
        exit(0)

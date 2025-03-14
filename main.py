from typing import List
import pronotepy
from api.cache.news import DISCUSSIONS_CACHE, NEWS_CACHE
from utils.debug_mode import debug_mode
from webhook.custom import send_custom_webhook
from webhook.discussions.discord import send_discord_discussions_webhook
from webhook.grades.discord import send_discord_grades_webhook
from webhook.news.discord import send_discord_news_webhook
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
                        await handler_webhook("grade",grade)
        except Exception as e:
            initialize_session()  # Reconnexion à Pronote en cas d'erreur
            print(f"Erreur pendant la vérification des notes : {e}")
        await asyncio.sleep(60)

async def check_for_new_news(session):
    """
    Vérifie périodiquement les nouvelles notes et envoie des notifications pour les ajouts.
    """
    while True:
        try:
            check_and_refresh_session()  # Vérification et rafraîchissement de la session
            for new in session.information_and_surveys(only_unread=True):
                if isinstance(new, pronotepy.Information):
                    
                    news_key = (
                        new.title,
                        new.author,
                        new.content,
                    )
                    if news_key not in NEWS_CACHE:
                        NEWS_CACHE.add(news_key)
                        if debug_mode():
                            print(f"Nouvelle actualité détectée : {new.title}")
                        await handler_webhook("news",new)
            for discussion in session.discussions(only_unread=True):
                if isinstance(discussion, pronotepy.Discussion):
                    discussion_key = (
                        discussion.subject,
                        discussion.creator,
                        discussion.messages[-1]
                    )
                    if discussion_key not in NEWS_CACHE:
                        DISCUSSIONS_CACHE.add(discussion_key)
                        if debug_mode():
                            print(f"Nouvelle discussion détectée : {discussion.subject}")
                        await handler_webhook("discussion",discussion)
        except Exception as e:
            initialize_session()
            print(f"Erreur pendant la vérification des actualités : {e}")
        await asyncio.sleep(60)

async def handler_check(session):
    """
    Vérifie périodiquement les nouvelles notes et actualités.
    """
    await asyncio.gather(check_for_new_grades(session), check_for_new_news(session))

async def handler_webhook(type_of: str, data):
    """
    Envoie des notifications pour une nouvelle note ou actualité à plusieurs webhooks.
    """
    callback_table = {
        "news": send_discord_news_webhook,
        "grade": send_discord_grades_webhook,
        "discussion": send_discord_discussions_webhook,
    }
    await asyncio.gather(send_custom_webhook(data), callback_table[type_of](data))


if __name__ == "__main__":
    asyncio.run(setup_cache_handler())
    print(
        "Initialisation terminée. Le programme surveille maintenant les nouvelles notes..."
    )
    try:
        asyncio.run(handler_check(session))
    except KeyboardInterrupt:
        print("Arrêt du programme.")
        input("Appuyez sur une touche pour quitter...")
        exit(0)

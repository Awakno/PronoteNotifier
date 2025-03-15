import pronotepy
import asyncio
from api.cache.news import DISCUSSIONS_CACHE, NEWS_CACHE
from api.cache.grades import GRADES_CACHE
from api.cache.handler import setup_cache_handler
from api.session import initialize_session, check_and_refresh_session, SESSION as session
from utils.debug_mode import debug_mode
from webhook.custom import send_custom_webhook
from webhook.discussions.discord import send_discord_discussions_webhook
from webhook.grades.discord import send_discord_grades_webhook
from webhook.news.discord import send_discord_news_webhook


async def check_for_updates(session, check_function, cache, handler_type):
    """
    Vérifie périodiquement les mises à jour (notes, actualités, discussions) et envoie des notifications.
    """
    while True:
        try:
            check_and_refresh_session()  # Vérification et rafraîchissement de la session
            await check_function(session, cache, handler_type)
        except Exception as e:
            initialize_session()  # Reconnexion à Pronote en cas d'erreur
            print(f"Erreur pendant la vérification ({handler_type}) : {e}")
        await asyncio.sleep(60)


async def check_grades(session, cache, handler_type):
    """
    Vérifie les nouvelles notes et envoie des notifications.
    """
    for period in session.periods:
        for grade in period.grades:
            grade_key = (period.name, grade.subject.name, grade.date.isoformat(), grade.grade)
            if grade_key not in cache:
                cache.add(grade_key)
                if debug_mode():
                    print(f"Nouvelle note détectée : {grade.subject.name} - {grade.grade}")
                await handler_webhook(handler_type, grade)


async def check_news_and_discussions(session, cache, handler_type):
    """
    Vérifie les nouvelles actualités et discussions, et envoie des notifications.
    """
    if handler_type == "news":
        items = session.information_and_surveys(only_unread=True)
    elif handler_type == "discussion":
        items = session.discussions(only_unread=True)
    else:
        return

    for item in items:
        if isinstance(item, pronotepy.Information) or isinstance(item, pronotepy.Discussion):
            item_key = (item.title if hasattr(item, "title") else item.subject,
                        item.author if hasattr(item, "author") else item.creator,
                        item.content if hasattr(item, "content") else item.messages[-1])
            if item_key not in cache:
                cache.add(item_key)
                if debug_mode():
                    print(f"Nouvelle {handler_type} détectée : {item.title if hasattr(item, 'title') else item.subject}")
                await handler_webhook(handler_type, item)


async def handler_webhook(type_of, data):
    """
    Envoie des notifications pour une nouvelle note ou actualité à plusieurs webhooks.
    """
    callback_table = {
        "news": send_discord_news_webhook,
        "grade": send_discord_grades_webhook,
        "discussion": send_discord_discussions_webhook,
    }
    await asyncio.gather(send_custom_webhook(data), callback_table[type_of](data))


async def main():
    """
    Point d'entrée principal pour surveiller les mises à jour.
    """
    await setup_cache_handler()
    print("Initialisation terminée. Le programme surveille maintenant les nouvelles notes...")
    try:
        await asyncio.gather(
            check_for_updates(session, check_grades, GRADES_CACHE, "grade"),
            check_for_updates(session, check_news_and_discussions, NEWS_CACHE, "news"),
            check_for_updates(session, check_news_and_discussions, DISCUSSIONS_CACHE, "discussion"),
        )
    except KeyboardInterrupt:
        print("Arrêt du programme.")
        input("Appuyez sur une touche pour quitter...")
        exit(0)


if __name__ == "__main__":
    asyncio.run(main())

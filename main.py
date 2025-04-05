from datetime import datetime
import asyncio
from api.cache.attendance import EDT_CACHE, check_edt
from api.cache.homeworks import HOMEWORKS_CACHE
from api.cache.news import DISCUSSIONS_CACHE, NEWS_CACHE
from api.cache.grades import GRADES_CACHE
from api.cache.handler import setup_cache_handler
from api.session import (
    initialize_session,
    check_and_refresh_session,
    SESSION as session,
)
from message.Status import Debug
from utils.debug_mode import debug_mode
from webhook.attendance.discord import send_discord_edt_webhook
from webhook.custom import send_custom_webhook
from webhook.discussions.discord import send_discord_discussions_webhook
from webhook.grades.discord import send_discord_grades_webhook
from webhook.homeworks.discord import send_discord_homeworks_webhook
from webhook.news.discord import send_discord_news_webhook

WEBHOOK_CALLBACKS = {
    "news": send_discord_news_webhook,
    "grade": send_discord_grades_webhook,
    "discussion": send_discord_discussions_webhook,
    "edt": send_discord_edt_webhook,
    "homework": send_discord_homeworks_webhook,
}


async def check_for_updates(session, check_function, cache, handler_type):
    """
    Vérifie périodiquement les mises à jour et envoie des notifications.
    """
    while True:
        try:
            check_and_refresh_session()
            await check_function(session, cache, handler_type)
        except Exception as e:
            initialize_session()
            print(f"Erreur ({handler_type}) : {e}")
        await asyncio.sleep(60)


async def check_grades(session, cache, handler_type):
    """Vérifie et notifie les nouvelles notes."""
    for period in session.periods:
        for grade in period.grades:
            grade_key = (
                period.name,
                grade.subject.name,
                grade.date.isoformat(),
                grade.grade,
            )
            if grade_key not in cache:
                cache.add(grade_key)
                log_debug("Nouvelle note", grade.subject.name, grade.grade)
                await send_notifications(handler_type, grade)


async def check_news_and_discussions(session, cache, handler_type):
    """Vérifie et notifie les nouvelles actualités et discussions."""
    items = (
        session.information_and_surveys(only_unread=True)
        if handler_type == "news"
        else session.discussions(only_unread=True)
    )

    for item in items:
        item_key = (
            getattr(item, "title", item.subject),
            getattr(item, "author", item.creator),
            getattr(item, "content", item.messages[-1]),
        )

        if item_key not in cache:
            cache.add(item_key)
            log_debug(f"Nouvelle {handler_type}", item_key[0])
            await send_notifications(handler_type, item)


async def check_edt_background(session, cache, handler_type):
    """Vérifie et notifie les mises à jour de l'emploi du temps."""
    actual_edt = check_edt(session)

    for hour in actual_edt:
        hour_key = (
            hour.id,
            hour.start,
            hour.end,
            hour.subject.name,
            tuple(hour.teacher_names),
            tuple(str(c) for c in hour.classrooms),
            hour.status,
            hour.canceled,
        )

        if hour_key not in cache:
            if hour_key[1] < datetime.now():
                continue

            cache.add(hour_key)
            if hour.status == "Exceptionnel":
                log_debug("Nouvel événement exceptionnel", hour.subject.name)
                await send_notifications(handler_type, hour)
            else:
                log_debug(
                    "Nouvel événement", hour.subject.name, hour.start, " - ", hour.end
                )

        else:
            cached_hour = next(
                (
                    c
                    for c in cache
                    if c[0] == hour.id and c[1] == hour.start and hour.end == c[2]
                ),
                None,
            )
            if cached_hour:
                changes = []
                if hour.start != cached_hour[1] or hour.end != cached_hour[2]:
                    changes.append("Changement d'heure")
                if hour.subject.name != cached_hour[3]:
                    changes.append("Changement de matière")
                if tuple(hour.teacher_names) != cached_hour[4]:
                    changes.append("Changement de professeur")
                if tuple(str(c) for c in hour.classrooms) != cached_hour[5]:
                    changes.append("Changement de salle")
                if hour.canceled != cached_hour[7]:
                    changes.append("Cours annulé")
                if hour.status != cached_hour[6]:
                    changes.append(f"Statut changé à {hour.status}")

                if changes:
                    cache.remove(cached_hour)
                    cache.add(hour_key)
                    for change in changes:
                        log_debug(change, hour.subject.name)
                    await send_notifications(handler_type, hour)

    EDT_CACHE.difference_update(
        {hour for hour in EDT_CACHE if hour[2] < datetime.now()}
    )


async def check_homeworks(session, cache, handler_type):
    """Vérifie et notifie les nouveaux devoirs."""
    for period in session.homework(date_from=datetime.now().date()):
        homework_key = (
            period.subject.name,
            period.date,
            period.description,
        )
        if homework_key not in cache:
            cache.add(homework_key)
            log_debug("Nouveau devoir", period.subject.name)
            await send_notifications(handler_type, period)


async def send_notifications(handler_type, data):
    """Envoie des notifications via les webhooks."""
    await asyncio.gather(
        send_custom_webhook(data), WEBHOOK_CALLBACKS[handler_type](data)
    )


def log_debug(message, *details):
    """Affiche un message de debug si activé."""
    if debug_mode():
        print(Debug(f"{message} - {details}"))


async def cleanup():
    """Clean up resources before exiting."""
    global session
    if session:
        session.communication.session.close()  # Close the Pronote session
    print("Resources cleaned up. Exiting...")


async def main():
    """Point d'entrée principal."""
    await setup_cache_handler()
    print("Initialisation terminée. Surveillance en cours...")
    try:
        await asyncio.gather(
            check_for_updates(session, check_grades, GRADES_CACHE, "grade"),
            check_for_updates(session, check_news_and_discussions, NEWS_CACHE, "news"),
            check_for_updates(
                session, check_news_and_discussions, DISCUSSIONS_CACHE, "discussion"
            ),
            check_for_updates(session, check_edt_background, EDT_CACHE, "edt"),
            check_for_updates(session, check_homeworks, HOMEWORKS_CACHE, "homework"),
        )
    except KeyboardInterrupt:
        print("Arrêt du programme.")
    finally:
        await cleanup()  # Ensure cleanup is called


if __name__ == "__main__":
    asyncio.run(main())

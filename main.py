from datetime import datetime
import asyncio
from api.cache.attendance import EDT_CACHE, check_edt
from api.cache.homeworks import HOMEWORKS_CACHE
from api.cache.news import DISCUSSIONS_CACHE, NEWS_CACHE
from api.cache.grades import GRADES_CACHE
from api.cache.handler import setup_cache_handler
from api import session as session_state
from api.session import initialize_session, check_and_refresh_session
from message.Status import Debug
from utils.debug_mode import debug_mode
from utils.env import get_env_variable
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

env = get_env_variable()


async def _disabled_noop(data):
    if debug_mode():
        print(Debug("Provider disabled"))
    return None


async def check_for_updates(check_function, cache, handler_type, *args):
    """
    Vérifie périodiquement les mises à jour et envoie des notifications.
    """
    while True:
        try:
            check_and_refresh_session()
            current_session = session_state.SESSION
            await check_function(current_session, cache, handler_type, *args)
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


def remove_latest_grade_from_cache():
    """Supprime la dernière note du cache pour forcer une notification (debug)."""
    if not GRADES_CACHE:
        return False
    # Trie par date ISO (YYYY-MM-DD) pour retirer la plus récente
    latest = max(GRADES_CACHE, key=lambda k: k[2])
    GRADES_CACHE.remove(latest)
    log_debug("Suppression forcée de la dernière note du cache", latest)
    return True


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


async def check_edt_background(session, cache, handler_type, days):
    """Vérifie et notifie les mises à jour de l'emploi du temps."""
    actual_edt = check_edt(session, days)

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
    import inspect

    tasks = []

    # custom webhook if configured
    if env.get("CUSTOM_WEBHOOK_URL") and env.get("CUSTOM_WEBHOOK_PASS"):
        tasks.append(send_custom_webhook(data))

    # Discord / provider callback
    cb = WEBHOOK_CALLBACKS.get(handler_type, _disabled_noop)
    try:
        cb_result = cb(data)
    except Exception:
        # If calling the callback raises synchronously, run it in a thread
        tasks.append(asyncio.to_thread(cb, data))
    else:
        if inspect.isawaitable(cb_result):
            tasks.append(cb_result)
        else:
            tasks.append(asyncio.to_thread(cb, data))

    # Telegram provider if configured
    if env.get("TELEGRAM_BOT_TOKEN") and env.get("TELEGRAM_CHAT_ID"):
        try:
            from webhook.telegram import send_telegram_message

            tasks.append(send_telegram_message(handler_type, data))
        except Exception:
            if debug_mode():
                print(Debug("Impossible d'importer le provider Telegram"))

    if tasks:
        await asyncio.gather(*tasks)


def log_debug(message, *details):
    """Affiche un message de debug si activé."""
    if debug_mode():
        print(Debug(f"{message} - {details}"))


async def cleanup():
    """Clean up resources before exiting."""
    if session_state.SESSION:
        session_state.SESSION.communication.session.close()  # Close the Pronote session
    print("Resources cleaned up. Exiting...")


async def main():
    """Point d'entrée principal."""
    env = get_env_variable()
    edt_days = int(env.get("PRONOTE_EDT_DAYS", 14))

    await setup_cache_handler()

    if debug_mode():
        remove_latest_grade_from_cache()

    print("Initialisation terminée. Surveillance en cours...")
    try:
        await asyncio.gather(
            check_for_updates(check_grades, GRADES_CACHE, "grade"),
            check_for_updates(check_news_and_discussions, NEWS_CACHE, "news"),
            check_for_updates(
                check_news_and_discussions, DISCUSSIONS_CACHE, "discussion"
            ),
            check_for_updates(check_edt_background, EDT_CACHE, "edt", edt_days),
            check_for_updates(check_homeworks, HOMEWORKS_CACHE, "homework"),
        )
    except KeyboardInterrupt:
        print("Arrêt du programme.")
    finally:
        await cleanup()  # Ensure cleanup is called


if __name__ == "__main__":
    asyncio.run(main())

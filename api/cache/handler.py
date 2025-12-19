import asyncio
import pronotepy
from api.cache import attendance, grades, news, homeworks
from api import session as session_state
from api.session import initialize_session
from message.Status import Info, Warning
from utils.env import get_env_variable


async def setup_cache_handler():
    """
    Configure le gestionnaire de cache.
    """

    env = get_env_variable()
    edt_days = int(env.get("PRONOTE_EDT_DAYS", 14))

    def handle_status(status, success_msg, failure_msg):
        if status:
            print(Info(success_msg))
        else:
            print(Warning(failure_msg))

    async def run_with_retry(func, *args):
        try:
            return await asyncio.to_thread(func, session_state.SESSION, *args)
        except pronotepy.exceptions.PronoteAPIError as exc:
            # Session expirée ou invalide : on réinitialise puis on retente une fois
            print(
                Warning(f"Session expirée pendant l'init ({exc}). Nouvelle session...")
            )
            initialize_session()
            return await asyncio.to_thread(func, session_state.SESSION, *args)

    news_status = await run_with_retry(news.initialize_news_cache)
    grade_status = await run_with_retry(grades.initialize_grades_cache)
    attendance_status = await run_with_retry(attendance.get_edt, edt_days)
    homework_status = await run_with_retry(homeworks.get_homeworks)

    news_cache_status, discussion_cache_status = news_status
    handle_status(
        news_cache_status,
        "Initialisation des actualités terminée.",
        "Aucune actualité détectée.",
    )
    handle_status(
        discussion_cache_status,
        "Initialisation des discussions terminée.",
        "Aucune discussion détectée.",
    )

    handle_status(
        grade_status, "Initialisation des notes terminée.", "Aucune note détectée."
    )

    handle_status(
        attendance_status,
        "Initialisation de l'emploi du temps terminée.",
        "Aucun événement détecté.",
    )

    handle_status(
        homework_status,
        "Initialisation des devoirs terminée.",
        "Aucun devoir détecté.",
    )

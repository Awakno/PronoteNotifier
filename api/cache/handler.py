from api.cache import attendance, grades, news, homeworks
from api.session import SESSION as session
from message.Status import Info, Warning


async def setup_cache_handler():
    """
    Configure le gestionnaire de cache.
    """

    def handle_status(status, success_msg, failure_msg):
        if status:
            print(Info(success_msg))
        else:
            print(Warning(failure_msg))

    news_status, discussion_status = news.initialize_news_cache(session)
    handle_status(
        news_status,
        "Initialisation des actualités terminée.",
        "Aucune actualité détectée.",
    )
    handle_status(
        discussion_status,
        "Initialisation des discussions terminée.",
        "Aucune discussion détectée.",
    )

    grade_status = grades.initialize_grades_cache(session)
    handle_status(
        grade_status, "Initialisation des notes terminée.", "Aucune note détectée."
    )

    attendance_status = attendance.get_edt(session)
    handle_status(
        attendance_status,
        "Initialisation de l'emploi du temps terminée.",
        "Aucun événement détecté.",
    )

    homework_status = homeworks.get_homeworks(session)
    handle_status(
        homework_status,
        "Initialisation des devoirs terminée.",
        "Aucun devoir détecté.",
    )

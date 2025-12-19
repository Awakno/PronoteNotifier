from datetime import datetime, timedelta
import pronotepy

EDT_CACHE = set()


def get_edt(session: pronotepy.Client, days: int = 14) -> bool:
    """Récupère l'emploi du temps et peuple le cache pour `days` jours."""
    for hour in session.lessons(
        date_from=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        date_to=datetime.today() + timedelta(days=days),
    ):

        hour_key = (
            hour.id,
            hour.start,
            hour.end,
            hour.subject.name,
            tuple(hour.teacher_names),
            tuple(str(classroom) for classroom in hour.classrooms),
            hour.status,
            hour.canceled,
        )
        if hour_key not in EDT_CACHE:
            EDT_CACHE.add(hour_key)

    return bool(EDT_CACHE)


def check_edt(session: pronotepy.Client, days: int = 14) -> list:
    """
    Vérifie les changements dans l'emploi du temps de l'utilisateur.
    """
    """Return the current list of lessons for the upcoming period.

    The caller (notification logic) compares these lessons against the
    `EDT_CACHE` set of keys to determine new or changed events.
    """
    lessons = []
    for hour in session.lessons(
        date_from=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        date_to=datetime.today() + timedelta(days=days),
    ):
        lessons.append(hour)

    return lessons

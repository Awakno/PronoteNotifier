from datetime import datetime
import pronotepy

HOMEWORKS_CACHE = set()


def get_homeworks(session: pronotepy.Client) -> list:
    """
    Récupère les devoirs à faire.
    """
    for period in session.homework(date_from=datetime.now().date()):
        homework_key = (
            period.subject.name,
            period.date,
            period.description,
        )
        if homework_key not in HOMEWORKS_CACHE:
            HOMEWORKS_CACHE.add(homework_key)
    return bool(HOMEWORKS_CACHE)

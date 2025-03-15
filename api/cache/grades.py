GRADES_CACHE = set()


def initialize_grades_cache(session):
    """
    Initialise le cache avec toutes les notes existantes sans envoyer de notifications.
    """
    GRADES_CACHE.update(
        {
            (
                period.name,
                grade.subject.name,
                grade.date.isoformat(),
                grade.grade,
            )
            for period in session.periods
            for grade in period.grades
        }
    )
    return bool(GRADES_CACHE)

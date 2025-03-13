GRADES_CACHE = set()


def initialize_grades_cache(session):
    """
    Initialise le cache avec toutes les notes existantes sans envoyer de notifications.
    """
    for period in session.periods:
        for grade in period.grades:
            # Ajout des notes sous forme d'une clé unique au cache
            grade_key = (
                period.name,
                grade.subject.name,
                grade.date.isoformat(),
                grade.grade,
            )
            GRADES_CACHE.add(grade_key)

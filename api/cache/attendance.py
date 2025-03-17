from datetime import datetime, timedelta
import pronotepy

EDT_CACHE = set()


def get_edt(session: pronotepy.Client) -> bool:
    """
    Récupère l'emploi du temps de l'utilisateur.
    """
    for hour in session.lessons(
        date_from=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0), date_to=datetime.today() + timedelta(days=28)
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


def check_edt(session: pronotepy.Client) -> list:
    """
    Vérifie les changements dans l'emploi du temps de l'utilisateur.
    """
    new_hours = set()
    for hour in session.lessons(
        date_from=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), 
        date_to=datetime.today() + timedelta(days=28)
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
        if hour_key not in new_hours:
            new_hours.add(hour)

    return new_hours

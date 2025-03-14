from api.cache import grades, news
from api.session import SESSION as session
from message.Status import Info, Warning


async def setup_cache_handler():
    """
    Configure le gestionnaire de cache.
    """
    news_status, discussion_status = news.initialize_news_cache(session)
    if not news_status:
        print(Warning("Aucune actualité détectée."))
    else:
        print(Info("Initialisation des actualités terminée."))
    if not discussion_status:
        print(Warning("Aucune discussion détectée."))
    else:
        print(Info("Initialisation des discussions terminée."))
    grade_status = grades.initialize_grades_cache(session)
    if not grade_status:
        print(Warning("Aucune note détectée."))
    else:
        print(Info("Initialisation des notes terminée."))

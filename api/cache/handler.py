from api.cache import grades
from api.session import SESSION as session


async def setup_cache_handler():
    """
    Configure le gestionnaire de cache.
    """
    grades.initialize_grades_cache(session)

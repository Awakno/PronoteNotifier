import pronotepy

NEWS_CACHE = set()
DISCUSSIONS_CACHE = set()


def initialize_news_cache(session: pronotepy.Client):
    """
    Initialise le cache des actualités.
    """
    for news in session.information_and_surveys(only_unread=True) + session.discussions(only_unread=True):
        if isinstance(news, pronotepy.Information):
            NEWS_CACHE.add((news.title, news.author, news.content))
        elif isinstance(news, pronotepy.Discussion):
            DISCUSSIONS_CACHE.add((news.subject, news.creator, news.messages[-1]))
        else:
            raise ValueError(f"Type d'actualité inconnu: {type(news)}")

    return bool(NEWS_CACHE), bool(DISCUSSIONS_CACHE)

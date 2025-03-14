import pronotepy

NEWS_CACHE = set()
DISCUSSIONS_CACHE = set()

def initialize_news_cache(session: pronotepy.Client):
    """
    Initialise le cache des actualités.
    """
    for news in [session.information_and_surveys(only_unread=True), session.discussions(only_unread=True)]:
        for new in news:
            if isinstance(new, pronotepy.Information):
                news_key = (
                    new.title,
                    new.author,
                    new.content,
                )
                NEWS_CACHE.add(news_key)
            elif isinstance(new, pronotepy.Discussion):
                discussion_key = (
                    new.subject,
                    new.creator,
                    new.messages[-1]
                )
                DISCUSSIONS_CACHE.add(discussion_key)
            else:
                raise ValueError("Type d'actualité inconnu, {}".format(type(new)))
    
    news_cache = True if len(NEWS_CACHE) > 0 else False
    discussions_cache = True if len(DISCUSSIONS_CACHE) > 0 else False
    return news_cache, discussions_cache

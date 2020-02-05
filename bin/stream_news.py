import fire
from mongoengine import connect
from tweepyrate import create_apps
import random
import tweepy
from hate_collector import TweetListener

default_queries = [
    "@infobae",
    "@LANACION",
    "@clarincom",
    "@cronica",
    "@perfilcom",
    #Diarios Españoles
    "@elmundoes",
    #Uruguayos
    "@elpaisuy",
    # Chilenos
    "@latercera", # Diario chileno
 ]


def stream_news(database, queries=default_queries):
    """
    Look for tweets mentioning (or from) any of these newspapers

    Arguments:
    ----------

    database: Name of the mongodatabase

    queries: list
        List of terms (or @usernames) to look for
    """
    apps = create_apps("config/my_apps.json")
    random.shuffle(apps)

    connect(database)

    print(f"Looking for {queries}")

    for i, word in enumerate(queries):
        app = apps[i % len(apps)]
        print(f"Creating listener for {word}")

        myStreamListener = TweetListener(word)
        myStream = tweepy.Stream(auth = app.auth, listener=myStreamListener)
        myStream.filter(track=[word], is_async=True, languages=["es"])


if __name__ == '__main__':
    fire.Fire(stream_news)

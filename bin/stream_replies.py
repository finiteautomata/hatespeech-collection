import fire
from mongoengine import connect
from tweepyrate import create_apps
import random
import tweepy
from hate_collector import ReplyListener

default_queries = ["racista", "misógino", "machista", "machirulo"]


def stream(database, queries=default_queries):
    """
    Look for replies using any of the words (queries)
    """
    apps = create_apps("config/my_apps.json")
    random.shuffle(apps)

    connect(database)


    print(f"Looking for {queries}")

    for i, word in enumerate(queries):
        app = apps[i % len(apps)]
        print(f"Creating listener for {word}")

        myStreamListener = ReplyListener(word)
        myStream = tweepy.Stream(auth = app.auth, listener=myStreamListener)
        myStream.filter(track=[word], is_async=True, languages=["es"])


if __name__ == '__main__':
    fire.Fire(stream)

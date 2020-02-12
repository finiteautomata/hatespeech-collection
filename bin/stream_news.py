import fire
from mongoengine import connect
from tweepyrate import create_apps
import random
import tweepy
import time
from queue import Queue
import threading
from hate_collector import TweetListener, TweetWorker

default_queries = [
    "@infobae",
    "@LANACION",
    "@clarincom",
    "@cronica",
    "@perfilcom",
    #Diarios Españoles
    "@elmundoes",
    "@lavanguardia",
    "@abc_es",
    #Uruguayos
    "@elpaisuy",
    # Chilenos
    "@latercera", # Diario chileno
 ]

def create_worker(queue):
    tweet_worker = TweetWorker()

    def worker():
        while True:
            status, query = queue.get(block=True)
            tweet_worker.work(status, query)
            queue.task_done()

    return worker


def stream_news(database, queries=default_queries, num_workers=3):
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

    # Create queue and workers
    print(f"Creating queue and {num_workers} workers")
    tweet_queue = Queue()
    threads = []
    for i in range(num_workers):
        t = threading.Thread(target=create_worker(tweet_queue))
        t.start()
        threads.append(t)



    for i, word in enumerate(queries):
        app = apps[i % len(apps)]
        print(f"Creating listener for {word}")

        myStreamListener = TweetListener(word, tweet_queue)
        myStream = tweepy.Stream(auth = app.auth, listener=myStreamListener)
        myStream.filter(track=[word], is_async=True, languages=["es"])


if __name__ == '__main__':
    fire.Fire(stream_news)

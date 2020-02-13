import fire
from mongoengine import connect
from tweepyrate import create_apps
import random
import tweepy
import time
from queue import Queue
import threading
from tweepyrate.streaming import create_queue, stream_query
from hate_collector import TweetWorker

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
    queue = create_queue(num_workers, TweetWorker)

    for i, word in enumerate(queries):
        app = apps[i % len(apps)]
        print(f"Creating listener for {word}")
        stream_query(word, app, queue, languages=["es"])


if __name__ == '__main__':
    fire.Fire(stream_news)

import fire
from mongoengine import connect
from tweepyrate import create_apps
import datetime
import time
import random
from collections import defaultdict
from tweepyrate.streaming import create_queue, stream_query
from hate_collector import TweetWorker

default_queries = [
    "@infobae",
    "@LANACION",
    "@clarincom",
    "@cronica",
    "@perfilcom",
    "@izquierdadiario",
    "@pagina12",
    #Diarios Españoles
    "@elmundoes",
    "@lavanguardia",
    "@abc_es",
    #Uruguayos
    "@elpaisuy",
    # Chilenos
    "@latercera", # Diario chileno
    # Diarios de derecha
    "@laderechadiario",
    #"@PrensaRepublica",
 ]




def stream_news(
    database, queries=default_queries, apps_file="config/my_apps.json",
    num_workers=3, report_secs=600):
    """
    Look for tweets mentioning (or from) any of these newspapers

    Arguments:
    ----------

    database: Name of the mongodatabase

    queries: list
        List of terms (or @usernames) to look for
    """
    apps = create_apps(apps_file)

    connect(database)

    print(f"Looking for {queries}")

    # Create queue and workers
    print(f"Creating queue and {num_workers} workers")
    queue = create_queue(num_workers, TweetWorker)
    listeners = []

    random.shuffle(queries)

    for i, word in enumerate(queries):
        app = apps[-(i+1) % len(apps)]
        print(f"Creating listener for {word} with {app.me().screen_name}")
        stream, listener = stream_query(word, app, queue, languages=["es"])
        listeners.append((stream, listener))

    last_count = defaultdict(int)
    time.sleep(report_secs)
    while True:
        # Print a report from time to time
        print("=" * 40 + '\n\n')
        print(datetime.datetime.now())

        new_count = 0
        for stream, listener in listeners:
            old_count = last_count[listener.query]
            last_count[listener.query] = listener.count
            new_tweets = last_count[listener.query] - old_count
            print(f"{listener.query:<25} -- {listener.count / 1000:.2f}K tweets ({new_tweets:<4} new tweets)")

            if new_tweets == 0:
                print("Restarting")
                stream.disconnect()
                stream.filter(track=[listener.query], is_async=True)

            new_count += new_tweets

        print(f"{new_count} new tweets")
        time.sleep(report_secs)

if __name__ == '__main__':
    fire.Fire(stream_news)

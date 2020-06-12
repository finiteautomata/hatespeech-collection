import os
import time
import threading
import fire
from multiprocessing import Pool
from tqdm.auto import tqdm
from mongoengine import NotUniqueError
import newspaper as ns
from hatespeech_models import Article, Tweet
from hate_collector.article import download_article
from hate_collector import connect_to_db
import queue
import tweepy



def create_article(tweet):
    if Article.objects(tweet_id=tweet["_id"]).count() > 0:
        # Already created, skipping
        return

    art = download_article(tweet)
    if not art:
        # Couldn't download
        return

    # Now ret should be a dict with "body" and "title" keys
    replies = Tweet.objects(in_reply_to_status_id=tweet["_id"]).as_pymongo()
    tweet["article"] = art
    tweet["replies"] = replies
    Article.from_tweet(tweet).save()

def generate_articles(database, num_workers=4, clean_before=False):
    """
    Generate articles
    """

    db = connect_to_db(database)
    print("Creating articles and their comments")

    if clean_before:
        print(f"Cleaning {Article.objects.count()} objects")
        Article.drop_collection()

    screen_names = [t[1:].lower() for t in db.tweet.distinct('query') if t is not None]
    print(f"Screen names: {' - '.join(screen_names)}")

    """
    Another approach: getting everything from the database at the
    very beginning. However, I'm getting stuck with the maximum db size of mongo
    """
    tweets = Tweet.objects(
        user_name__in=screen_names,
        in_reply_to_status_id=None,
        retweeted_status=None
    ).as_pymongo()
    #tweets = list(tweets)
    print(f"There are {tweets.count()/1000:.2f}K news\n\n")
    print("Creating articles...")

    pbar = tqdm(total=len(tweets))
    q = queue.Queue()
    stopping = threading.Event()

    def worker(timeout=1):
        db = connect_to_db(database)
        while not stopping.is_set():
            try:
                tweet = q.get(True, timeout)
                create_article(tweet)
                pbar.update()

                q.task_done()
            except queue.Empty:
                pass

    threads = []
    print(f"Creating {num_workers} threads")
    for i in range(num_workers):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for tw in tweets:
        q.put(tw)

    q.join()
    stopping.set()
    print(f"There are {Article.objects.count()} instances")

if __name__ == '__main__':
    fire.Fire(generate_articles)

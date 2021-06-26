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



def create_article(tweet, save_without_article):
    if Article.objects(tweet_id=tweet["_id"]).count() > 0:
        # Already created, skipping
        return

    art = download_article(tweet)
    if not art and not save_without_article:
        # Couldn't download
        return

    # Now ret should be a dict with "body" and "title" keys
    replies = Tweet.objects(in_reply_to_status_id=tweet["_id"]).as_pymongo()
    tweet["article"] = art
    tweet["replies"] = replies
    Article.from_tweet(tweet).save()

def should_process(tweet):
    return not tweet.get("in_reply_to_status_id", None) and not tweet.get("retweeted_status", None)

def generate_articles(database, num_workers=4, clean_before=False, screen_names=None, save_without_article=True):
    """
    Generate articles
    """

    db = connect_to_db(database)
    print("Creating articles and their comments")

    if clean_before:
        print(f"Cleaning {Article.objects.count()} objects")
        inp = input("Type yes to confirm: ")
        if inp != "yes":
            print("Cancelling")
            return
        Article.drop_collection()

    if screen_names is None:
        screen_names = [t[1:].lower() for t in db.tweet.distinct('query') if t is not None]
    print(f"Screen names: {' - '.join(screen_names)}")

    """
    Another approach: getting everything from the database at the
    very beginning. However, I'm getting stuck with the maximum db size of mongo
    """
    tweets = Tweet.objects(
        user_name__in=screen_names,
    ).order_by("-created_at").as_pymongo()
    #tweets = list(tweets)
    print(f"There are {tweets.count()/1000:.2f}K news\n\n")
    print("Creating articles...")
    pbar = tqdm(total=tweets.count())
    q = queue.Queue()
    stopping = threading.Event()

    def worker(timeout=1):
        db = connect_to_db(database)
        while not stopping.is_set():
            try:
                tweet = q.get(True, timeout)

                if should_process(tweet):
                    create_article(tweet, save_without_article)

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

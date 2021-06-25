import os
import time
import threading
import fire
from multiprocessing import Pool
from tqdm.auto import tqdm
import newspaper as ns
import asyncio
from hate_collector.article import download_article
from hate_collector import connect_to_db
import queue
import motor.motor_asyncio


async download_article

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

def should_process(tweet):
    return not tweet.get("in_reply_to_status_id", None) and not tweet.get("retweeted_status", None)

async def process_tweet(tweet, db):
    if should_process(tweet):
        """
        Process
        """
        replies = db.tweet.find({"in_reply_to_status_id": tweet["_id"]})

        async for reply in replies:
            pass

async def worker(name, queue, db, pbar):
    while True:
        tweet = await queue.get()
        await process_tweet(tweet, db)
        pbar.update()
        queue.task_done()

async def main(database, screen_names, num_workers):
    client = motor.motor_asyncio.AsyncIOMotorClient()
    db = client[database]

    print(f"Connected to {database}")

    print("Creating articles and their comments")


    if screen_names is None:
        screen_names = [t[1:].lower() for t in (await db.tweet.distinct('query')) if t is not None]
    print(f"Screen names: {' - '.join(screen_names)}")

    query = {
        "user_name": {"$in": screen_names},
        # It takes a long time to search for this
        # Do not know why as there are indices
        # "in_reply_to_status_id": None,

        #"retweeted_status": None,
    }
    total_tweets = await db.tweet.count_documents(query)

    print(f"Tweets: {total_tweets /1e6:.2f}M")
    print(f"Fetching tweets...")
    queue = asyncio.Queue()
    pbar = tqdm(total=total_tweets)


    async for tweet in db.tweet.find(query):
        queue.put_nowait(tweet)
        pbar.update()


    print("Creating workers")

    pbar = tqdm(total=total_tweets)
    """
    Create tasks
    """
    tasks = []
    for i in range(num_workers):
        task = asyncio.create_task(
            worker(f"worker-{i}", queue, db, pbar)
        )
        tasks.append(task)

    print("Processing")
    await queue.join()

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)


def generate_articles(database, screen_names=None, num_workers=10):
    """
    Generate articles (using asyncio)
    """
    asyncio.run(main(database, screen_names, num_workers))

if __name__ == '__main__':
    fire.Fire(generate_articles)

import os
import time
import fire
from multiprocessing import Pool
from mongoengine import connect
from tqdm.auto import tqdm
import newspaper as ns
from hatespeech_models import Article, Tweet
from hate_collector.article import download_article
import tweepy

def connect_to_mongo(database):
    mongo_host = os.environ.get("MONGO_HOST", 'localhost')
    mongo_port = os.environ.get("MONGO_PORT", 27017)

    print(f"Connecting to {mongo_host}:{mongo_port} - db : {database}")
    client = connect(database)
    return client[database]


def download_article_and_replies(tweet):
    art = download_article(tweet)
    # Now ret should be a dict with "body" and "title" keys
    replies = Tweet.objects(in_reply_to_status_id=tweet["_id"]).as_pymongo()

    return (art, replies)

def download_articles(tweets, num_workers):
    with Pool(num_workers) as p:
        total = len(tweets)
        articles = list(tqdm(p.imap(download_article_and_replies, tweets), total=total))

        for tw, (art, replies) in zip(tweets, articles):
            if art:
                tw["article"] = art
                tw["replies"] = replies


def generate_instances(database, num_workers=4, clean_before=True, rebuild=True):
    """
    Generate instances for annotation
    """

    db = connect_to_mongo(database)
    print("Creating articles and their comments")

    if clean_before:
        print(f"Cleaning {Article.objects.count()} objects")
        Article.drop_collection()

    screen_names = [t[1:].lower() for t in db.tweet.distinct('query') if t is not None]
    print(f"Screen names: {' - '.join(screen_names)}")

    """
    This is another approach: getting everything from the database at the
    very beginning. However, I'm getting stuck with the maximum db size of mongo
    begin = time.time()
    tweets = db.tweet.aggregate([
        {
            "$match": {
                "user_name": {"$in": screen_names },
                "in_reply_to_status_id": None,
                "retweeted_status": None,
            }
        },
        {
            "$lookup": {
                "from": "tweet",
                "localField": "_id",
                "foreignField": "in_reply_to_status_id",
                "as": "replies"
            }
        },
        {
            "$unwind": "$replies"
        }
    ])
    """
    tweets = Tweet.objects(
        user_name__in=screen_names,
        in_reply_to_status_id=None,
        retweeted_status=None
    ).as_pymongo()
    tweets = list(tweets)
    print(f"There are {len(tweets)/1000:.2f}K news\n\n")
    print("Searching for articles...")
    download_articles(tweets, num_workers)
    # Now "article" should be in each tweet
    non_empty_arts = [tweet for tweet in tweets if "article" in tweet]
    len_replies = len([1 for tweet in non_empty_arts for reply in tweet["replies"]])

    print(f"There are {len(non_empty_arts)/1000:.2f}K non-empty articles and {len_replies/1000:.2f}K replies")

    print("Saving instances...")
    for tweet in tqdm(non_empty_arts):
        art = Article.from_tweet(tweet)
        art.save()

    print(f"There are {Article.objects.count()} instances")

if __name__ == '__main__':
    fire.Fire(generate_instances)

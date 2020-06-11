import os
import time
import fire
from multiprocessing import Pool
from tqdm.auto import tqdm
from mongoengine import NotUniqueError
import newspaper as ns
from hatespeech_models import Article, Tweet
from hate_collector.article import download_article
from hate_collector import connect_to_db
import tweepy


def download_article_and_replies(tweet):
    art = download_article(tweet)
    # Now ret should be a dict with "body" and "title" keys
    replies = Tweet.objects(in_reply_to_status_id=tweet["_id"]).as_pymongo()

    return (art, replies)


def generate_articles(database, num_workers=4, clean_before=True):
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

    new_arts = 0
    new_replies = 0

    with Pool(num_workers) as p:
        total = len(tweets)
        articles = tqdm(p.imap(download_article_and_replies, tweets), total=total)

        for tw, (art, replies) in zip(tweets, articles):
            try:
                if Article.objects(tweet_id=tw.id).count() > 0:
                    continue
                if art:
                    tw["article"] = art
                    tw["replies"] = replies
                    Article.from_tweet(tw).save()
                    new_arts += 1
                    new_replies += len(replies)
            except NotUniqueError as e:
                pass

    print("f{}")
    print(f"There are {Article.objects.count()} instances")

if __name__ == '__main__':
    fire.Fire(generate_articles)

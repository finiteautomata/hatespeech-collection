from itertools import cycle
from mongoengine import connect
from tweepyrate import create_apps
import fire
import tweepy
from multiprocessing import Pool
from tqdm import tqdm
from hate_collector.models import Tweet

def fetch_and_save(*args):
    # TODO: Fix this. I don't know why I should do this way
    app, tweet_id = args[0]
    try:
        status = app.get_status(tweet_id, tweet_mode="extended")
        tweet = Tweet(**status._json)
        tweet.save()
        return (tweet_id, tweet)
    except tweepy.TweepError as e:
        return (tweet_id, e)


def fetch_tweets(apps, tweet_ids):
    with Pool(len(apps)) as p:
        pbar = tqdm(total=len(tweet_ids))

        def update_pbar(*args, **kwargs):
            pbar.update()

        iterator = p.imap(
            fetch_and_save,
            zip(cycle(apps), tweet_ids)
        )

        # This hack is just to make tqdm work.
        list(tqdm(iterator, total=len(tweet_ids)))


def find_upstream_tweets(database):
    """
    Look for tweets whose replies are within our database
    """
    apps = create_apps("config/my_apps.json")

    connect(database)

    replies = Tweet.objects(
        in_reply_to_status_id__exists= True,
        in_reply_to_status_id__ne= None,
    )

    upstream_ids = [t.in_reply_to_status_id for t in replies]

    print(f"\nThere are {len(replies)} replies in our database")

    upstream_in_db = Tweet.objects(id__in=upstream_ids)
    ids_in_db = set(t.id for t in upstream_in_db)

    print(f"{len(ids_in_db)} of upstream already in database")

    tweet_ids = [tid for tid in upstream_ids if tid not in ids_in_db]

    fetch_tweets(apps, tweet_ids)



if __name__ == '__main__':
    fire.Fire(find_upstream_tweets)

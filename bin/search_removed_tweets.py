import time
from itertools import cycle
from multiprocessing import Pool
from tqdm import tqdm
from mongoengine import connect, ValidationError, NotUniqueError
from tweepyrate import create_apps
import fire
import tweepy
from hate_collector.models import Tweet, APIError

def fetch_and_save(*args):
    # TODO: Fix this. I don't know why I should do this way
    app, tweet_id = args[0]
    try:
        status = app.get_status(tweet_id, tweet_mode="extended")
        return (tweet_id, status)
    except tweepy.TweepError as e:
        return (tweet_id, e)


def fetch_errors(apps, tweet_ids):
    with Pool(len(apps)) as p:
        iterator = p.imap(
            fetch_and_save,
            zip(cycle(apps), tweet_ids)
        )

        # This hack is just to make tqdm work.
        ret = list(tqdm(iterator, total=len(tweet_ids)))

        print("Saving just errors")
        new_errors = 0
        for tweet_id, response in ret:
            if type(response) is tweepy.TweepError:
                try:
                    error = APIError(
                        message=str(response),
                        api_code=response.api_code,
                        tweet_id=tweet_id
                    )

                    error.save()

                    new_errors += 1
                except (NotUniqueError, ValidationError) as e:
                    continue
        print(f"There are {new_errors} new errors")



def search_removed_tweets(database):
    """
    Search for tweets that have been removed or whose users have been suspended
    """
    apps = create_apps("config/my_apps.json")

    connect(database)

    tweets = Tweet.objects(
        query=None,
    )

    tweet_ids = [tw.id for tw in tweets]

    print(f"\nThere are {tweets.count()} to look for in our database")
    fetch_errors(apps, tweet_ids)


if __name__ == '__main__':
    fire.Fire(search_removed_tweets)

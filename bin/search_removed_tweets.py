import time
from itertools import cycle
from multiprocessing import Pool
from mongoengine import connect, ValidationError, NotUniqueError
from tweepyrate import create_apps, get_tweets
import fire
import tweepy
from hate_collector.models import Tweet, APIError


def save_error(tweet_id, response):
    try:
        error = APIError(
            message=str(response),
            api_code=response.api_code,
            tweet_id=tweet_id
        )

        error.save()

    except (NotUniqueError, ValidationError) as e:
        pass
    except ValidationError as e:
        print(e)



def fetch_errors(apps, tweet_ids):
    new_tweets, new_errors = get_tweets(
        apps,
        tweet_ids,
        lambda _1, _2: None,
        save_error,
    )

    print(f"There are {new_tweets} new tweets and {new_errors} new errors")

def search_removed_tweets(database):
    """
    Search for tweets that have been removed or whose users have been suspended
    """
    apps = create_apps("config/my_apps.json")

    client = connect(database)
    db = client[database]

    tweets = db.tweet.find(
        { "query": None },
        { "_id": 1 },
    )

    tweet_ids = [tw["_id"] for tw in tweets]

    print(f"\nThere are {tweets.count()} to look for in our database")
    fetch_errors(apps, tweet_ids)


if __name__ == '__main__':
    fire.Fire(search_removed_tweets)

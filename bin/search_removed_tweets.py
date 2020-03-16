import datetime
from mongoengine import connect, ValidationError, NotUniqueError
from tweepyrate import create_apps, get_tweets
import fire
import tweepy
from hatespeech_models import Tweet, APIError


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

def update_tweet(tweet_id, response):
    # There was no error => update tweet
    tweet = Tweet.objects.get(id=tweet_id)

    tweet.last_checked_for_errors = datetime.datetime.utcnow()
    tweet.save()



def fetch_errors(apps, tweet_ids):
    new_tweets, new_errors = get_tweets(
        apps,
        tweet_ids,
        update_tweet,
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

    print("Looking for tweets without errors...")
    tweets_without_errors = db.tweet.aggregate([
        {
            "$lookup": {
                "from": "api_error",
                "localField": "_id",
                "foreignField": "tweet_id",
                "as": "errors"
            }
        },
        {
            "$match": {
                "errors": {"$size": 0 },
            }
        },
    ])

    # Get the ids
    tweet_ids = [tw["_id"] for tw in tweets_without_errors]

    print(f"\nThere are {len(tweet_ids)} to look for in our database")
    fetch_errors(apps, tweet_ids)


if __name__ == '__main__':
    fire.Fire(search_removed_tweets)

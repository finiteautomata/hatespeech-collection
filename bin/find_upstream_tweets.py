import time
from collections import defaultdict
from mongoengine import connect, ValidationError, NotUniqueError
from tweepyrate import create_apps, get_tweets
import fire
import tweepy
from hate_collector.models import Tweet, APIError


class ResponseProcess:
    def __init__(self, tweet_to_replies):
        self.tweet_to_replies = tweet_to_replies

    def process_tweet(self, tweet_id, response):
        try:
            tweet = Tweet(**response._json)
            tweet.save()

            self._mark_replies_as_processed(tweet_id)
        except (ValidationError, NotUniqueError) as e:
            pass

    def process_error(self, tweet_id, response):
        try:
            error = APIError(
                message=str(response),
                api_code=response.api_code,
                tweet_id=tweet_id
            )

            error.save()

            self._mark_replies_as_processed(tweet_id)
        except NotUniqueError as e:
            pass
        except ValidationError as e:
            print("Error without api_code")
            print(e)

    def _mark_replies_as_processed(self, tweet_id):
        """
        Sets look_for_upstream=False for every
        """
        for reply in self.tweet_to_replies[tweet_id]:
            reply.look_for_upstream = False
            reply.save()

def search_for_nonprocessed_tweets(apps, db):
    # Look for tweets that needs processing
    replies = Tweet.objects(look_for_upstream=True)
    print(f"Looking upstream tweets for {len(replies)} tweets")

    upstream_ids = set(t.in_reply_to_status_id for t in replies)
    print(f"Tweets to look for: {len(upstream_ids)}")

    ## Beware! Do not check those already having errors
    errors = db.api_error.find({
        "tweet_id": {"$in": list(upstream_ids)}},
        {"tweet_id": 1}
    )
    error_tweet_ids = set(err["tweet_id"] for err in errors)
    upstream_ids = upstream_ids.difference(error_tweet_ids)

    print(f"Tweets without errors: {len(upstream_ids)}")

    tweet_to_replies = defaultdict(list)
    for reply in replies:
        tweet_to_replies[reply.in_reply_to_status_id].append(reply)

    processor = ResponseProcess(tweet_to_replies)

    new_tweets, new_errors = get_tweets(
        apps,
        list(upstream_ids),
        processor.process_tweet,
        processor.process_error,
    )

    print(f"There are {new_tweets} new tweets and {new_errors} new errors")


def find_upstream_tweets(database, sleep_time=300):
    """
    Look for tweets whose replies are within our database
    """
    apps = create_apps("config/my_apps.json")

    client = connect(database)
    db = client[database]

    epoch = 0

    while True:
        print(f"{'='*40}\n" * 3)
        print(f"Epoch number {epoch}\n")

        search_for_nonprocessed_tweets(apps, db)

        print(f"Sleeping for {sleep_time} seconds")
        time.sleep(sleep_time)

        epoch += 1



if __name__ == '__main__':
    fire.Fire(find_upstream_tweets)

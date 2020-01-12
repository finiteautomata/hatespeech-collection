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
        tweet = Tweet(**status._json)
        # I don't save it here because pymongo is not threadsafe
        #tweet.save()
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
        ret = list(tqdm(iterator, total=len(tweet_ids)))

        print("Saving tweets and errors")
        new_tweets = 0
        new_errors = 0
        for tweet_id, response in ret:
            if type(response) is Tweet:
                try:
                    tweet = response
                    tweet.save()
                    new_tweets += 1
                except (ValidationError, NotUniqueError) as e:
                    continue
            elif type(response) is tweepy.TweepError:
                try:
                    error = APIError(
                        message=str(response),
                        api_code=response.api_code,
                        tweet_id=tweet_id
                    )
                    
                    error.save()
                    
                    new_errors += 1
                except NotUniqueError as e:
                    continue
        print(f"There are {new_tweets} new tweets and {new_errors} new errors")



def find_upstream_tweets(database, sleep_time=300):
    """
    Look for tweets whose replies are within our database
    """
    apps = create_apps("config/my_apps.json")

    connect(database)
    epoch = 0

    while True:
        print(f"{'='*40}\n" * 3)
        print(f"Epoch number {epoch}")

        replies = Tweet.objects(
            in_reply_to_status_id__exists= True,
            in_reply_to_status_id__ne= None,
        )

        upstream_ids = [t.in_reply_to_status_id for t in replies]
        print(f"\nThere are {len(replies)} replies in our database")

        upstream_in_db = Tweet.objects(id__in=upstream_ids)
        ids_in_db = set(t.id for t in upstream_in_db)

        print(f"{len(ids_in_db)} of upstream already in database")

        not_in_db = [tid for tid in upstream_ids if tid not in ids_in_db]

        # Last: is there any of those with already known errors?
        
        tweets_with_errors = APIError.objects(tweet_id__in=not_in_db)
        error_ids = set(t.id for t in tweets_with_errors)
        
        without_errors = [tid for tid in not_in_db if tid not in error_ids]
        
        print(f"{len(without_errors)} tweets are without any error")
        fetch_tweets(apps, without_errors)

        print(f"Sleeping for {sleep_time} seconds")
        time.sleep(sleep_time)

        epoch += 1



if __name__ == '__main__':
    fire.Fire(find_upstream_tweets)

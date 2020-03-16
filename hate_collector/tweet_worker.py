import tweepy
from mongoengine import NotUniqueError
from hatespeech_models import Tweet

class TweetWorker:
    def __init__(self, only_replies=False, tweet_class=Tweet):
        self._only_replies = only_replies
        # This is only for testing purposes
        self._tweet_class = tweet_class

    def work(self, status, query):
        try:
            if self._only_replies and not status.in_reply_to_status_id:
                return
            tweet = self._tweet_class(**status._json)
            tweet.query = query

            tweet.save()
        except NotUniqueError as e:
            pass

import tweepy
from mongoengine import NotUniqueError
from .models import Tweet

class TweetListener(tweepy.StreamListener):
    def __init__(self, query, only_replies=False, tweet_class=Tweet):
        self._count = 0
        self.query = query
        self._only_replies = only_replies
        self._replies = 0
        # This is only for testing purposes
        self._tweet_class = tweet_class

        super().__init__()

    def on_status(self, status):
        try:
            if self._only_replies and not status.in_reply_to_status_id:
                return
            self._count += 1
            tweet = self._tweet_class(**status._json)
            tweet.query = self.query

            tweet.save()
            if status.in_reply_to_status_id:
                self._replies += 1

            if self._count % 500 == 0:
                print(f"{self._count / 1000:.2f}K tweets bajados sobre {self.query}")
                print(f"{self._replies / 1000:.2f}K respuestas")
        except NotUniqueError as e:
            pass

    def on_error(self, status_code):
        print(f"Error tipo: {status_code} para query {self.query}")
        print("Tenemos que esperar...")
        return True

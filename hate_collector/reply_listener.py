import tweepy
from mongoengine import NotUniqueError
from .models import Tweet

class ReplyListener(tweepy.StreamListener):
    def __init__(self, query):
        self._count = 0
        self._replies = 0
        self.query = query

        super().__init__()

    def on_status(self, status):
        try:
            self._count += 1

            if status.in_reply_to_status_id:
                tweet = Tweet(**status._json)
                tweet.query = self.query

                tweet.save()
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

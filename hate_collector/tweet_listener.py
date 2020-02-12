import tweepy
from mongoengine import NotUniqueError
from .models import Tweet

class TweetListener(tweepy.StreamListener):
    """
    Listener of Twitter Streaming API

    This class does not do any real time processing. It just pushes the
    received status to the respective queue, so another processes do the

    We do this to avoid being overwhelmed by the stream. See this link for further information:

    https://github.com/tweepy/tweepy/issues/448
    """
    def __init__(self, query, queue):
        self.query = query
        self.queue = queue
        super().__init__()

    def on_status(self, status):
        self.queue.put((status, self.query))

    def on_error(self, status_code):
        print(f"Error tipo: {status_code} para query {self.query}")
        print("Tenemos que esperar...")
        return True

"""
Entrypoint for hate_collector
"""
from .tweet_worker import TweetWorker
from .connection import connect_to_db

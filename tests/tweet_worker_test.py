import pytest
from unittest.mock import MagicMock
from hate_collector import TweetWorker

@pytest.fixture
def created_tweet():
    return MagicMock()

@pytest.fixture
def not_reply_status():
    return MagicMock(in_reply_to_status_id=None)

@pytest.fixture
def reply_status():
    return MagicMock(in_reply_to_status_id=123)

@pytest.fixture
def tweet_worker():
    return TweetWorker()

def test_creates_with_zero_counts(tweet_worker):
    assert tweet_worker._count == 0
    assert tweet_worker._replies == 0

def test_creates_only_replies_flag():
    tweet_worker = TweetWorker(only_replies=True)
    assert tweet_worker._only_replies

def test_work_saves_if_not_reply(created_tweet, not_reply_status):
    def my_mock_tweet_class(*args, **kwargs):
        return created_tweet

    listener = TweetWorker(
        only_replies=False, tweet_class=my_mock_tweet_class
    )

    listener.work(not_reply_status, "query")

    created_tweet.save.assert_called_with()

def test_work_saves_if_reply(created_tweet, reply_status):
    def my_mock_tweet_class(*args, **kwargs):
        return created_tweet

    listener = TweetWorker(
        only_replies=False, tweet_class=my_mock_tweet_class
    )

    listener.work(reply_status, "query")

    created_tweet.save.assert_called_with()

def test_work_not_saves_if_not_reply_and_only_replies(created_tweet, not_reply_status):
    def my_mock_tweet_class(*args, **kwargs):
        return created_tweet

    listener = TweetWorker(
        only_replies=True, tweet_class=my_mock_tweet_class
    )

    listener.work(not_reply_status, "query")

    created_tweet.save.assert_not_called()

def test_work_saves_if_reply_and_only_replies(created_tweet, reply_status):
    def my_mock_tweet_class(*args, **kwargs):
        return created_tweet

    listener = TweetWorker(
        only_replies=True, tweet_class=my_mock_tweet_class
    )

    listener.work(reply_status, "reply")

    created_tweet.save.assert_called_with()

import pytest
from unittest.mock import MagicMock
from hate_collector import TweetListener

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
def tweet_listener():
    return TweetListener("query")

def test_creates_with_zero_counts(tweet_listener):
    assert tweet_listener._count == 0
    assert tweet_listener._replies == 0

def test_creates_only_replies_flag():
    tweet_listener = TweetListener("query", only_replies=True)
    assert tweet_listener._only_replies

def test_on_status_saves_if_not_reply(created_tweet, not_reply_status):
    def my_mock_tweet_class(*args, **kwargs):
        return created_tweet

    listener = TweetListener(
        "query", only_replies=False, tweet_class=my_mock_tweet_class
    )

    listener.on_status(not_reply_status)

    created_tweet.save.assert_called_with()

def test_on_status_saves_if_reply(created_tweet, reply_status):
    def my_mock_tweet_class(*args, **kwargs):
        return created_tweet

    listener = TweetListener(
        "query", only_replies=False, tweet_class=my_mock_tweet_class
    )

    listener.on_status(reply_status)

    created_tweet.save.assert_called_with()

def test_on_status_not_saves_if_not_reply_and_only_replies(created_tweet, not_reply_status):
    def my_mock_tweet_class(*args, **kwargs):
        return created_tweet

    listener = TweetListener(
        "query", only_replies=True, tweet_class=my_mock_tweet_class
    )

    listener.on_status(not_reply_status)

    created_tweet.save.assert_not_called()

def test_on_status_saves_if_reply_and_only_replies(created_tweet, reply_status):
    def my_mock_tweet_class(*args, **kwargs):
        return created_tweet

    listener = TweetListener(
        "query", only_replies=True, tweet_class=my_mock_tweet_class
    )

    listener.on_status(reply_status)

    created_tweet.save.assert_called_with()

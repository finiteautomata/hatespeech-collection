import pytest
from unittest.mock import MagicMock
from hate_collector import TweetListener

@pytest.fixture
def status():
    return MagicMock()

@pytest.fixture
def queue():
    return MagicMock()

@pytest.fixture
def tweet_listener(queue):
    return TweetListener("query", queue)

def test_creates_with_query_and_queue(queue):
    listener = TweetListener("query", queue)

    assert listener.query == "query"
    assert listener.queue == queue

def test_pushes_to_queue_query_and_item(tweet_listener, queue, status):
    tweet_listener.on_status(status)

    queue.put.assert_called_with((status, "query"))

def test_on_error_returns_true(tweet_listener):
    assert tweet_listener.on_error(404)

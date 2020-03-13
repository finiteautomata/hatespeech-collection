import pytest
from datetime import datetime, timedelta
from mongoengine import connect
from hate_collector.models import Article, Comment

comment_id = 0
def comment():
    global comment_id
    comment_id += 1
    return Comment(
        tweet_id=comment_id,
        text=f"Comment no {comment_id}"
    )

client = None
db = None
db_name = "hatespeech-test"

def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    global client
    global db

    client = connect(db_name)
    db = client[db_name]

def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    client.drop_database(db_name)


def test_create_article():
    art = Article(
        tweet_id = 12345,
        text = "This is a tweet",
        body = "This is a detailed explanation of the news",
        created_at=datetime.utcnow() - timedelta(days=1),
    )
    comments = [comment(), comment()]

    art.comments = comments

    art.save()

    art = Article.objects.get(tweet_id=12345)

    assert len(art.comments) == 2
    assert art.comments[0].text == comments[0].text
    assert art.comments[1].text == comments[1].text

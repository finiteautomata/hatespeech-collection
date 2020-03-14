import datetime
from mongoengine import (
    DynamicDocument,
    EmbeddedDocument,
    StringField,
    ListField,
    DateTimeField,
    LongField,
    BooleanField,
    EmbeddedDocumentField,
)


class Comment(EmbeddedDocument):
    tweet_id = LongField(required=True)
    text = StringField(required=True)

class Article(DynamicDocument):
    tweet_id = LongField(required=True, unique=True)
    text = StringField(required=True, max_length=500)
    created_at = DateTimeField(required=True)
    body = StringField(required=True)
    comments = ListField(EmbeddedDocumentField(Comment))

    @classmethod
    def from_tweet(cls, tweet):
        article = cls(
            tweet_id=tweet["_id"],
            created_at=tweet["created_at"],
            text=tweet["text"],
            body=tweet["article"],
        )

        article.comments = []

        for reply in tweet["replies"]:
            article.comments.append(Comment(
                tweet_id=reply["_id"],
                text=reply["text"],
            ))

        return article

    meta = {
        'indexes': [
            {
                'fields': ['$body', "$text"],
                'default_language': 'spanish',
            },
        ]
    }

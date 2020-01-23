import datetime
from mongoengine import (
    DynamicDocument,
    StringField,
    DateTimeField,
    LongField,
)

class APIError(DynamicDocument):
    """
    This model help us track API errors while retrieving tweets.
    Tracking these is helpful to recover statuses containing possibly hate speech

    """
    message = StringField()
    api_code = LongField(required=True)
    tweet_id = LongField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'indexes': [
            'api_code',
            'tweet_id',
        ],
        'collection': 'api_error',
    }

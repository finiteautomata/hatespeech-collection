import datetime
from mongoengine import (
    DoesNotExist,
    DynamicDocument,
    StringField,
    DateTimeField,
    LongField,
    BooleanField,
    signals
)

class Tweet(DynamicDocument):
    text = StringField()
    id = LongField(primary_key=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    last_checked_for_errors = DateTimeField(default=datetime.datetime.utcnow)
    # This field represents if we should check
    look_for_upstream = BooleanField(default=True)
    interesting = BooleanField(default=False, required=True)
    checked = BooleanField(default=False, required=True)

    in_reply_to_status_id = LongField()
    meta = {
        'indexes': [
            {
                'fields': ['$text'],
                'default_language': 'spanish',
            },
            'query',
            'look_for_upstream',
            'in_reply_to_status_id',
            'created_at',
            'checked',
            'last_checked_for_errors',
            'interesting',
        ]
    }

def update_text(sender, document):
    tweet = document
    try:
        tweet.text = tweet.full_text
    except AttributeError:
        try:
            tweet.text = tweet.extended_tweet["full_text"]
        except AttributeError:
            pass

def check_upstream(sender, document):
    tweet = document
    try:
        #
        # If there is no upstream tweet => do no check
        if tweet.in_reply_to_status_id:
            # Check out if upstream tweet is on db
            Tweet.objects.get(id=tweet.in_reply_to_status_id)
        tweet.look_for_upstream = False
    except DoesNotExist as e:
        tweet.look_for_upstream = True


signals.pre_save.connect(update_text, sender=Tweet)
signals.pre_save.connect(check_upstream, sender=Tweet)

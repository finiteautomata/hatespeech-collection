from mongoengine import (
    DynamicDocument,
    StringField,
    DateTimeField,
    LongField,
    signals
)

class Tweet(DynamicDocument):
    text = StringField(max_length=500)
    id = LongField(primary_key=True)
    created_at = DateTimeField()


def update_text(sender, document):
    tweet = document
    try:
        tweet.text = tweet.extended_tweet["full_text"]
    except AttributeError:
        pass


signals.pre_save.connect(update_text, sender=Tweet)

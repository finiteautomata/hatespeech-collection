import fire
from multiprocessing import Pool
from mongoengine import connect
from tqdm.auto import tqdm
from newspaper import Article, ArticleException
from hate_collector import models
import tweepy

def download_article(tweet):
    try:
        if "article" in tweet:
            return
        news_url = tweet["entities"]["urls"][0]["expanded_url"]
        article = Article(news_url)
        article.download()
        article.parse()
        if len(article.text) > 0:
            return article.text
    except (KeyError, IndexError) as e:
        pass
    except ArticleException as e:
        pass
    return None


def download_articles(tweets, num_workers):
    with Pool(num_workers) as p:
        total = len(tweets)
        articles = list(tqdm(p.imap(download_article, tweets), total=total))

        for tw, art in zip(tweets, articles):
            if art:
                tw["article"] = art

def create_article(tweet):
    art = models.Article.from_tweet(tweet)

    art.save()

    return art


def generate_instances(database, num_workers=4):
    """
    Generate instances for annotation
    """

    client = connect(database)
    db = client[database]
    print(f"Looking for possibly hateful news and their comments")

    screen_names = [t[1:].lower() for t in db.tweet.distinct('query') if t is not None]
    print(f"Screen names: {' - '.join(screen_names)}")
    tweets = db.tweet.aggregate([
        {
            "$match": {
                "user_name": {"$in": screen_names },
                "possibly_hateful_comments": True
            }
        },
        {
            "$lookup": {
                "from": "tweet",
                "localField": "_id",
                "foreignField": "in_reply_to_status_id",
                "as": "replies"
            }
        },
    ])

    tweets = list(tweets)
    len_replies = len([1 for tweet in tweets for reply in tweet["replies"]])
    print(f"There are {len(tweets)/1000:.2f}K tweets and {len_replies/1000:.2f}K replies\n\n")

    print("Searching for articles...")
    download_articles(tweets, num_workers)
    # Now "article" should be in each tweet
    non_empty_arts = [tweet for tweet in tweets if "article" in tweet]
    len_replies = len([1 for tweet in non_empty_arts for reply in tweet["replies"]])

    print(f"There are {len(non_empty_arts)/1000:.2f}K non-empty articles and {len_replies/1000:.2f}K replies")

    print("Saving instances...")
    for tweet in tqdm(non_empty_arts):
        create_article(tweet)
    print(f"There are {models.Article.objects.count()} instances")

if __name__ == '__main__':
    fire.Fire(generate_instances)

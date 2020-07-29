import os
import time
import threading
import fire
from tqdm.auto import tqdm
import lxml
from mongoengine import ValidationError
from hatespeech_models import Article, Tweet
from hate_collector.article import body_getters
from hate_collector import connect_to_db
import queue

def correct_text(database, num_workers=4):
    """
    Generate articles
    """
    media = list(body_getters.keys())
    print(f"Correcting {media} texts")
    db = connect_to_db(database)

    articles = Article.objects(user__in=media).only("id")
    pbar = tqdm(total=articles.count())
    q = queue.Queue()
    stopping = threading.Event()

    def worker(timeout=1):
        db = connect_to_db(database)
        while not stopping.is_set():
            try:
                article_id = q.get(True, timeout)

                article = Article.objects.get(id=article_id)
                doc = lxml.html.fromstring(article.html)

                article.body = body_getters[article.user](doc)
                article.save()
                pbar.update()

                q.task_done()
            except queue.Empty:
                pass
            except ValidationError as e:
                print(e)
                q.task_done()
            except IndexError as e:
                print(e)
                print(article.tweet_id)
                q.task_done()


    threads = []
    print(f"Creating {num_workers} threads")
    for i in range(num_workers):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for art in articles:
        q.put(str(art.id))
    #for tw in tweets:
    #    q.put(tw)

    q.join()
    stopping.set()

if __name__ == '__main__':
    fire.Fire(correct_text)

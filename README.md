# Collecting Hate Speech content


## Install

We need `python >= 3.6` and `pipenv`. Also, `mongodb` is needed.

1. Install requirements

```
pipenv shell
pipenv sync
```

2. Download submodules

```
git submodule update
pipenv install -e tweepyrate/
```


### Stream tweets commenting about news


```
python bin/stream_news.py --database DATABASE_NAME
```

This will stream tweets mentioning major news in Spanish. You can change that
by using `--queries`


### Streaming replies

```
python bin/stream_replies.py --database DATABASE_NAME --queries [facha,facho,fascista,machirulo,machista,misogino,racista]
```

### Search upstream

It is also important to look for tweets "upstream"; that is, if I retrieve a tweet B that is a reply to another tweet A, we would like to look for it too.

To do this, run:

```
python bin/find_upstream_tweets.py --database DATABASE_NAME
```

A daemon will start that incrementally searchs for upstream tweets. Tweets already processed are "marked"; errors for tweets that cannot be retrieved are saved in collection `api_error`.

### Search for deleted or banned tweets

It is also important to look for tweets that have been removed, banned, whose users protected them, etc. To do that:

```
python bin/search_removed_tweets.py --database DATABASE_NAME
```

This will save errors in `api_error` collection. A list of codes can be found [here](https://developer.twitter.com/en/docs/basics/response-codes)


### Marking news as possibly hateful

`Tweet` model has a `possibly_hateful_comments` field which is meant to be filled by another apps by marking those news possibly having some mysoginistic or racist comment.

### Downloading news

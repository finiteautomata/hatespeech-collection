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

3. Put tokens in `config/`

(such as in `config/my_apps.json.template`)

4. Start downloading news
```
python bin/stream_news.py --database DATABASE_NAME --apps_file APP_FILE
```

Meanwhile, download upstream tweets

```
python bin/find_upstream_tweets.py --database DATABASE_NAME --apps_file APP_FILE
```

5. Mark news having possibly hateful comments

With a third-party app, mark some "news" as having possibly hateful comments. We mark them by setting `possibly_hateful_comments` in `Tweet` class

Notice that we have no clear distinction

5. Generate instances for labelling

Once you consider you have enough news marked as having possibly hateful comments, run the following command:

```
python bin/generate_instances.py --database DATABASE_NAME
```

This will look for tweets having `user_name` of those in the queries (default: @lanacion, @infobae, etc) and marked with the flag `possibly_hateful_comments`. With those tweets, it will try to download and parse the respective news (following links in the original tweet) and finally it will generate another collection called `articles` having documents with this fashion

```
{
  "tweet_id": <id of the tweet generating the news>
  "text": <text of the tweet>
  "body": <text of the news>
  "comments": [
      {
        "tweet_id": <tweet_id of comment>
        "text": <text of tweet>
      }
  ]
}
```

6. Generate dumps

If we want to export the database, we can use `mongodump` and `mongoexport` tools:

```
# This generates a mongo bson dump
mongodump --db DB --collection article --out dumps/
# To generate a JSON file:
mongoexport -d hatespeech-news -c article --jsonArray --pretty  --out dumps/hatespeech-articles.json
```

If you want to create a specific dump for coronavirus, you can use

```
python bin/generate_release.py <DATABASE_NAME> <QUERY_FILE> <OUT>
```

For instance...

```
python bin/generate_release.py hatespeech-news config/query_2.0.json dumps/coronavirus-v2.json
```

Also, you can just use `mongoexport`

```
mongoexport -d <DATABASE> -c article --jsonArray --pretty \
--query <QUERY> \
--fields 'tweet_id,text,slug,title,url,user,body,created_at,comments' \
--out dumps/coronavirus-argentina-v1.1.json
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


### Dumping database

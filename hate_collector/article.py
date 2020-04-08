import newspaper as ns

def _download_infobae(article):
    """
    Checked at: 8 Apr 2020
    newspaper cannot parse properly infobae => let's do it manually!

    Everything seems to be under this div#article-content
    """
    elem = article.doc.get_element_by_id("article-content")

    text = ""
    for par in elem.iter("p"):
        children = list(par)
        if len(children) > 0:
            text += " ".join([c.text or '' for c in children])
        elif par.text:
            text += par.text
        else:
            continue
        text += "\n"

    article.text = text

def download_article(tweet):
    """
    Download newspaper.Article for a single tweet

    Returns None if can't be downloaded
    """
    try:
        if "article" in tweet:
            return
        news_url = tweet["entities"]["urls"][0]["expanded_url"]
        user_name = tweet["user"]["screen_name"]

        article = ns.Article(news_url)
        article.download()
        article.parse()

        if user_name == "infobae":
            _download_infobae(article)
        if len(article.text) > 0:
            return {
                "body" : article.text,
                "title": article.title,
            }
    except (KeyError, IndexError) as e:
        pass
    except ns.ArticleException as e:
        pass
    return None

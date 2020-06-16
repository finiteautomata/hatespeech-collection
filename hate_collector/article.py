import newspaper as ns

def __get_text_infobae(doc):
    """
    Checked at: 16 Jun 2020
    newspaper cannot parse properly infobae => let's do it manually!

    Everything seems to be under this div#article-content
    """
    elem = doc.get_element_by_id("article-content")

    """
    Esto es código particular de infobae
    Saco los links que están al pie de la nota
    """
    children = list(elem.getchildren())

    last = children[-1]

    while len(list(children[-1].iter("a"))) > 0:
        children.pop(-1)

    """
    Me quedo con el texto
    """
    text_children = [t for t in children if t.tag not in ["meta", "script"]]
    text = "\n\n".join(t.text_content().strip() for t in text_children)

    return text

body_getters = {
    "infobae": __get_text_infobae,
}

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
            article.text = __get_text_infobae(article.doc)
        if len(article.text) > 0:
            return {
                "body" : article.text,
                "title": article.title,
                "url": article.url,
                'html': article.html,
            }
    except (KeyError, IndexError) as e:
        pass
    except ns.ArticleException as e:
        pass
    return None

from hate_collector.article import body_getters
from newspaper import Article as NSArticle


def test_it_gets_the_correct_text():
    url = "https://www.infobae.com/america/deportes/futbol-europeo/2020/07/31/la-llamativa-nueva-camiseta-que-estreno-el-barcelona-con-un-color-que-utilizara-por-tercera-vez-en-su-historia/"

    article = NSArticle(url, language="es")

    article.download()
    article.parse()

    text = body_getters["infobae"](article.doc)

    assert "El FC Barcelona" in text

from django.shortcuts import render
from django.http import HttpResponse
from .amazonPublisher import AmazonPublisher
import time

amazon_publisher = AmazonPublisher()


# Create your views here.
def home_page(request):

    display_articles = _retrieve_next_news(request)
    last_timestamp = _calculate_last_timestamp(display_articles)

    return render(request, "newsHome/home.html", {'articles': display_articles, 'last_timestamp': last_timestamp})


def archive_page(request):

    display_articles = _retrieve_next_news(request, 'oldNews')
    last_timestamp = _calculate_last_timestamp(display_articles)

    return render(request, "newsHome/archive.html", {'articles': display_articles, 'last_timestamp': last_timestamp})


def _retrieve_next_news(request, news_type: str = 'actualNews'):
    article_timestamp = request.GET.get('article_timestamp')

    if article_timestamp is None:
        article_timestamp = int(time.time() * 1000000)
    else:
        article_timestamp = int(article_timestamp)

    return amazon_publisher.retrieve_messages_from_dynamodb(article_timestamp, news_type, 5)


def _calculate_last_timestamp(display_articles):
    if len(display_articles) == 0:
        return -1
    else:
        return display_articles[-1]['date_published']

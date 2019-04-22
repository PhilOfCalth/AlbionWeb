from django.shortcuts import render
from django.http import HttpResponse
from .amazonPublisher import AmazonPublisher
import time


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

amazon_publisher = AmazonPublisher()


# Create your views here.
def home_page(request):

    article_timestamp = request.GET.get('article_timestamp')

    if article_timestamp is None:
        article_timestamp = int(time.time() * 1000000)
    else :
        article_timestamp = int(article_timestamp)

    display_articles = amazon_publisher.retrieve_messages_from_dynamodb(article_timestamp,  5)

    if len(display_articles) == 0 :
        last_timestamp = -1
    else:
        last_timestamp = display_articles[-1]['date_published']

    return render(request, "newsHome/home.html", {'articles': display_articles, 'last_timestamp': last_timestamp})

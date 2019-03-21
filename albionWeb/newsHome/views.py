from django.shortcuts import render
from django.http import HttpResponse
import boto3
from datetime import datetime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

_all_articles = None

def _init_articles():
    global _all_articles

    if None == _all_articles :
        amazon_publisher = AmazonPublisher()
        _all_articles = amazon_publisher.retrieve_messages_from_queue(10)

    # article_1 = {"MessageAttributes":
    #     {
    #         "captured_date": {"StringValue": "2019-Mar-02", "DataType": "String"},
    #         "link": {"StringValue": "http://www.modiphius.com/modiphius-press-releases/forbidden-lands-launches",
    #                  "DataType": "String"},
    #         "title": {"StringValue": "Forbidden Lands Launches!", "DataType": "String"},
    #         "website": {"StringValue": "https://www.modiphius.com/4/feed", "DataType": "String"}
    #     },
    #     "MessageBody": "Modiphius has announced the release of a brand new RPG, Forbidden Lands. This is new take on classic fantasy roleplaying. In this open-world survival roleplaying game, you’re not heroes sent on missions dictated by others - instead, you are raiders and rogues bent on making your own mark on a cursed world. ",
    # }
    #
    # article_2 = {"MessageAttributes":
    #     {
    #         "captured_date": {"StringValue": "2019-Mar-01", "DataType": "String"},
    #         "link": {"StringValue": "http://www.google.co.uk",
    #                  "DataType": "String"},
    #         "image": {"DataType": "String",
    #                   "StringValue": "https://koboldpress.com/wp-content/uploads/2019/01/WL009_WorldTree-1-193x300.jpg"},
    #         "title": {"StringValue": "This is google!", "DataType": "String"},
    #         "website": {"StringValue": "http://www.google.co.uk", "DataType": "String"}
    #     },
    #     "MessageBody": "Google google google!",
    # }
    #
    # article_3 = {"MessageAttributes":
    #     {
    #         "captured_date": {"StringValue": "2019-Mar-01", "DataType": "String"},
    #         "link": {"StringValue": "https://www.fantasyflightgames.com/en/news/2019/2/25/a-phantom-menace/",
    #                  "DataType": "String"},
    #         "image": {"DataType": "String",
    #                   "StringValue": "https://images-cdn.fantasyflightgames.com/filer_public/47/c7/47c7503e-03d8-4445-89e8-1987d3d7cb89/swz30_preview1.jpg"},
    #         "title": {"StringValue": "X wing second edition stuff!", "DataType": "String"},
    #         "website": {"StringValue": "http://www.google.co.uk", "DataType": "String"}
    #     },
    #     "MessageBody": "Well done referencing the worst movie ever!",
    # }
    #
    # _all_articles = [article_1, article_2, article_3]
    #
    # for i in range(1000):
    #     _all_articles.append({"MessageAttributes":
    #         {
    #             "captured_date": {"StringValue": "2019-Mar-01", "DataType": "String"},
    #             "link": {"StringValue": "https://www.fantasyflightgames.com/en/news/2019/2/25/a-phantom-menace/",
    #                      "DataType": "String"},
    #             "image": {"DataType": "String",
    #                       "StringValue": "https://images-cdn.fantasyflightgames.com/filer_public/47/c7/47c7503e-03d8-4445-89e8-1987d3d7cb89/swz30_preview1.jpg"},
    #             "title": {"StringValue": "X wing second edition stuff!", "DataType": "String"},
    #             "website": {"StringValue": "http://www.google.co.uk", "DataType": "String"}
    #         },
    #         "MessageBody": f"Well done referencing the worst movie ever! # {i} #",
    #     })


# Create your views here.
def home_page(request):

    article_number = request.GET.get('article_number', 1)

    _init_articles()

    paginator = Paginator(_all_articles, 5)

    try:
        display_articles = paginator.page(article_number)
    except PageNotAnInteger:
        display_articles = paginator.page(1)
    except EmptyPage:
        display_articles = paginator.page(paginator.num_pages)

    return render(request, "newsHome/home.html", {'articles': display_articles})


class AmazonPublisher(object):
    def __init__(self):
        self.sqs = boto3.client('sqs', region_name='eu-west-1', aws_access_key_id="AKIAIVKPXFTVTPS7JAMQ",
                                aws_secret_access_key="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")
        self.queue_url = 'https://sqs.eu-west-1.amazonaws.com/185394215596/AlbionActualNewsQueue.fifo'

    def add_message_to_queue(self, title: str, blurb: str, link: str, image: str, website: str) -> str:

        filled_title = title if None is not title and '' != title else "N/A"
        filled_image = image if None is not image and '' != image else "N/A"
        filled_blurb = blurb if None is not blurb and '' != blurb else "N/A"

        # Send message to SQS queue
        response = self.sqs.send_message(
            QueueUrl=self.queue_url,
            DelaySeconds=10,
            MessageAttributes={
                'title': {
                    'DataType': 'String',
                    'StringValue': filled_title
                },
                'link': {
                    'DataType': 'String',
                    'StringValue': link
                },
                'image': {
                    'DataType': 'String',
                    'StringValue': filled_image
                },
                'website': {
                    'DataType': 'String',
                    'StringValue': website
                },
                'captured_date': {
                    'DataType': 'String',
                    'StringValue': datetime.now().strftime("%Y-%b-%d")
                }
            },
            MessageBody=(
                filled_blurb
            )
        )

        return response['MessageId']

    def retrieve_messages_from_queue(self, quantity: int = 1) -> list:
        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=quantity,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        return response['Messages']

    def delete_message(self, receipt_handle: str):
        # Delete received message from queue
        if None is not receipt_handle:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )

from django.shortcuts import render
from django.http import HttpResponse
import boto3
from datetime import datetime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

_all_articles = None

def _init_articles():
    global _all_articles

    #if None == _all_articles :
    amazon_publisher = AmazonPublisher()
    _all_articles = amazon_publisher.retrieve_messages_from_queue(10)


# Create your views here.
def home_page(request):

    article_number = request.GET.get('article_number')

    if article_number is None:
        _init_articles()
        article_number = 1

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

        messages = response.get('Messages')
        if messages is None:
            return []
        return messages

    def delete_message(self, receipt_handle: str):
        # Delete received message from queue
        if None is not receipt_handle:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )

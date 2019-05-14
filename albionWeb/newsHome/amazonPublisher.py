import boto3
import os
from boto3.dynamodb.conditions import Key

class AmazonPublisher(object):
    def __init__(self):
        asw_key = os.environ['ALBION_USER_KEY']
        aws_pass = os.environ['ALBION_USER_PASS']

        self.dynamo_table = boto3.resource('dynamodb', region_name='eu-west-1', aws_access_key_id=asw_key,
                                aws_secret_access_key=aws_pass)\
                            .Table('news')

    def put_item_in_dynamo(self, item : map):
        response = self.dynamo_table.put_item(
            Item=item
        )

    def retrieve_messages_from_dynamodb(self, start_time : int, news_type: str = 'actualNews', quantity: int = 1) -> list:
#        response = self.bck_dynamo_table.scan(FilterExpression=Key('date_published').lt(start_time), Limit=quantity)
        response = self.dynamo_table.query(KeyConditionExpression=Key('type').eq(news_type) & Key('date_published').lt(start_time),
                                           ScanIndexForward=False,
                                           Limit=quantity)
        items = response[u'Items']
        if items is None:
            return []
        return items


if __name__ == "__main__":
    import time

    article_timestamp = int(time.time() * 1000000)
    #article_timestamp = 1555708244838 #1555707950386 #1555707512954
    amazon_pub = AmazonPublisher()
    items = amazon_pub.retrieve_messages_from_dynamodb(article_timestamp, 3)
    print("done")
    # for item in items:
    #     # del item["id"]
    #     # item['type'] = "actualNews"
    #     amazon_pub.put_item_in_dynamo(item)

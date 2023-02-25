from email.mime import image
import boto3
import image_classification
import json
import os
f = open('aws_config.json')
global config
config = json.load(f)
global sqs_client, s3_client
sqs_client = boto3.client("sqs", region_name=config['region'])
s3_client = boto3.client("s3", region_name=config["region"], aws_access_key_id=config["AccessKeyID"],aws_secret_access_key=config["SecretAccessKey"])

from botocore.exceptions import ClientError
import json

request_queue_url = config['RequestSQS']
response_queue_url = config['ResponseSQS']

def read_queue():

    # Receive message from SQS queue
    response = sqs_client.receive_message(
        QueueUrl=request_queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=20,
        WaitTimeSeconds=10
    )
    if "Messages" not in response:
        print('No messages')
        return
    message = response['Messages'][0]
    print("message: " + str(message))
    receipt_handle = message['ReceiptHandle']

    # Delete received message from queue
    sqs_client.delete_message(
        QueueUrl=request_queue_url,
        ReceiptHandle=receipt_handle
    )
    return json.loads(message['Body'])

class Message():
    def __init__(self, id, image, classification):
        self.id = id
        self.image = image
        self.classification = classification

def process_image(message):
    print(message)
    image_name = message['inputBucketKey']
    s3_client.download_file(config['InputS3'], image_name, 'images/' + image_name)
    classification = image_classification.classify('images/' + image_name)

    s3_client.put_object(
        Bucket = config['OutputS3'],
        Key = image_name.split('.')[0]+'.txt',
        Body = str(classification)
    )

    message = Message(message['id'], image_name, classification)
    sqs_client.send_message(
        QueueUrl=response_queue_url,
        MessageBody=str(json.dumps(message.__dict__))
    )
    print(message.image + " processed. Classification - " + classification)

if __name__ == "__main__":
    if not os.path.exists("images"):
        os.makedirs("images")

    while True:
        message = read_queue()
        if message:
            process_image(message)
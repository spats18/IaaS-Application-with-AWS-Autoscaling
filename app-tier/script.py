#!/usr/bin/env python3
from email.mime import image
import boto3
import image_classification
import json
import os

f = open('aws_config.json')
global config
config = json.load(f)
global sqs_client, s3_client
sqs_client = boto3.client("sqs", region_name=config['region'], aws_access_key_id=config["AccessKeyID"],aws_secret_access_key=config["SecretAccessKey"])
s3_client = boto3.client("s3", region_name=config["region"], aws_access_key_id=config["AccessKeyID"],aws_secret_access_key=config["SecretAccessKey"])

from botocore.exceptions import ClientError
import json

request_queue_url = config['RequestSQS']
response_queue_url = config['ResponseSQS']

# New Functions
def long_poll_sqs():
    '''
    Long polling the SQS and get one message at a time
    '''
    response_obj = sqs_client.receive_message(QueueUrl=request_queue_url, MaxNumberOfMessages=1, VisibilityTimeout=20,WaitTimeSeconds=10)
    print('Response Object', response_obj)
    if "Messages" not in response_obj:
        print('No messages')
        return
    message_response = response_obj['Messages'][0]
#     print('message received')
    message_body = message_response['Body']
    print('Message Body',message_body)
    delete_message(message_response)
    return json.loads(message_body)

def delete_message(message: dict):
    '''
    Delete the input message from SQS queue
    '''
    delete_response = sqs_client.delete_message(QueueUrl=request_queue_url, ReceiptHandle=message['ReceiptHandle'])
    print(delete_response)

def send_sqs_message(messageId: str, image_name: str, result: str):
    message_object = Message(messageId, image_name, result)
    sqs_client.send_message(QueueUrl=response_queue_url,MessageBody=str(json.dumps(message_object.__dict__)))
    print(message_object.image + " processed. Classification - " + message_object.classification)

def upload_result(image_name: str, result: str):
    '''
    Put a file/object to S3 bucket
    '''
    put_response = s3_client.put_object(Body='({},{})'.format(image_name, result),Bucket=config['OutputS3'],Key=image_name.split('.')[0]+'.txt')
    print(put_response)
    return(put_response)

def download_image(image_name: str):
    '''
    Download the image from S3 bucket
    '''
    s3_client.download_file(config['InputS3'], image_name, 'images/' + image_name)

def classification_process(message):
    print(message)
    image_name = message['inputBucketKey']
    download_image(image_name)
    image_path = 'images/' + image_name
    classification_result = image_classification.classify(image_path)
    send_sqs_message(message['id'], image_name, classification_result)
    return (image_name, classification_result)


class Message():
    def __init__(self, id, image, classification):
        self.id = id
        self.image = image
        self.classification = classification

if __name__ == "__main__":
    if not os.path.exists("images"):
        os.makedirs("images")

    while True:
        message = long_poll_sqs()
        print('Mesasge polled from SQS', message)
        if message:
            print(type(message))
            image_name, classification_result = classification_process(message)
            upload_result(image_name, classification_result)
            send_sqs_message(message['id'], image_name, classification_result)
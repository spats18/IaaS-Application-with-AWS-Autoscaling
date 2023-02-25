from email.mime import image
import boto3
from classifier import image_classification
import json
import os
from dotenv import load_dotenv

load_dotenv('../key.env')

f = open('aws_config.json')
global config
config = json.load(f) 

from botocore.exceptions import ClientError
import json

# Create SQS client
sqs = boto3.client("sqs", region_name=config['region'],
        aws_access_key_id=config["AccessKeyID"],
                       aws_secret_access_key=config["SecretAccessKey"])
s3 = boto3.client("s3", region_name=config['region'],
        aws_access_key_id=config["AccessKeyID"],
                       aws_secret_access_key=config["SecretAccessKey"])
# asg_client = boto3.client('autoscaling', region_name=config['region'],
#         aws_access_key_id=config["AccessKeyID"],
#                        aws_secret_access_key=config["SecretAccessKey"])
# cw_client = boto3.client('cloudwatch', region_name=config['region'],
#         aws_access_key_id=config["AccessKeyID"],
#                        aws_secret_access_key=config["SecretAccessKey"])

request_queue_url = config['RequestSQS']
response_queue_url = config['ResponseSQS']

def read_queue():

    # Receive message from SQS queue
    try:
        response = sqs.receive_message(QueueUrl=request_queue_url,AttributeNames=['SentTimestamp'],MaxNumberOfMessages=1,MessageAttributeNames=['All'],VisibilityTimeout=20,WaitTimeSeconds=10)
    except Exception as e:
        print(e) 
    
    if "Messages" not in response:
        print('No messages')
        return
    message = response['Messages'][0]
    print("message: " + str(message))
    receipt_handle = message['ReceiptHandle']
    print(receipt_handle)
    # Delete received message from queue
    # sqs.delete_message(
    #     QueueUrl=request_queue_url,
    #     ReceiptHandle=receipt_handle
    # )
    return json.loads(message['Body'])

class Message():
    def __init__(self, id, image, classification):
        self.id = id
        self.image = image
        self.classification = classification

def process_image(message):
    print(message)
    s3.download_file(config['InputS3'], message['name'], 'downloads/'+message['name'])
    classification = image_classification.classify('downloads/'+message['name'])

    s3.put_object(
        Bucket = config['OutputS3'],
        Key = message['name'].split('.')[0],
        Body = str({
            message['name'].split('.')[0]: classification
        })
    )

    message = Message(message['id'], message['name'], classification)
    sqs.send_message(
        QueueUrl=config['ResponseSQS'],
        MessageBody=str(json.dumps(message.__dict__))
    )
    print(message.image + " processed. Classification - " + classification)

if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    print(response_queue_url, request_queue_url)
    message = read_queue()
    # while True:
        # message = read_queue()
        # if message:
            # process_image(message)


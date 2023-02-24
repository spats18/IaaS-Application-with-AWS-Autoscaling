import boto3
from botocore.exceptions import ClientError
import json, os, pathlib
f = open('aws_config.json')
global config
config = json.load(f)
global sqs_client, s3_client
sqs_client = boto3.client("sqs", region_name=config['region'])
s3_client = boto3.client("s3", region_name=config["region"], aws_access_key_id=config["AccessKeyID"],aws_secret_access_key=config["SecretAccessKey"])

def check_request_queue_message(input_sqs: str):
    '''
    Long polling the SQS and get one message at a time
    '''
    request_sqs_url = 'https://sqs.{}.amazonaws.com/{}/{}'.format(config['region'], config['AccountID'], input_sqs)
    response_obj = sqs_client.receive_message(QueueUrl=request_sqs_url, MaxNumberOfMessages=1, WaitTimeSeconds=15)
    message = dict(response_obj['Messages'][0])
    delete_message(message)
    return message

def delete_message(message: dict):
    '''
    Delete the message from SQS queue
    '''
    # print(message)
    # print(message['Body'])
    # print(message['ReceiptHandle'])
    request_sqs_url = 'https://sqs.{}.amazonaws.com/{}/{}'.format(config['region'], config['AccountID'], config['RequestSQS'])
    delete_response = sqs_client.delete_message(QueueUrl=request_sqs_url, ReceiptHandle=message['ReceiptHandle'])
    
def put_object(input_s3: str, filename: str):
    '''
    Put a file/object to S3 bucket
    '''
    # put a file 
    # file_obj = os.path.join(pathlib.Path(__file__).parent.resolve(), filename)
    # put_response = s3_client.put_object(Body=file_obj,Bucket=input_s3,Key=filename) 
    # Put a key value pair
    put_response = s3_client.put_object(Body=filename,Bucket=input_s3,Key=filename) 
    # print(put_response)
    return(put_response)

def send_message(input_sqs: str):
    request_sqs_url = 'https://sqs.{}.amazonaws.com/{}/{}'.format(config['region'], config['AccountID'], input_sqs)
    


if __name__ == "__main__":
    sqs_request_file = check_request_queue_message(config["RequestSQS"])
    print(sqs_request_file)
    x = put_object(config['OutputS3'], "images/test_0.JPEG")
    # print(x)


'''
SQS Message
{
    'MessageId': '7f3cb5e0-06e9-4e62-bf7f-d91e0bbbc9de', 
    'ReceiptHandle': 'AQEBOwRfxIu1fos1FWbejGwbUTmOpw4e+baaHoiEvynAhjxeseZPkbrZe2yj1/TUgrqnS/LRZ58MA7FdlUbsdL6blT8thAvz2IzelrLJoRU+y/efLc/JMtr+pZ5qTAXie3qGqZa/BGUDkJoYlpdzfLmHgfHIxkU5eEXe2LObj/rpIMnBjaohqK/NaXiqrcuPFbtqHpvrFpg3BnW29rIPQVRmgBM+hqSRGQtkUw0jHCJeF7iC4qdrDeY24WVs5hAnwmq4VvAFUSYiAjovqypW58/eNx/h/Io82qROxSGqolAzAlyYF/QgztUcngGJfYE+1x7UgDDT6PCHpn2E2je3Erm0wLlSgmedvcaL9/I2zRxQiJTPDcluy3BL+PoZV+9b44vF2V8ptOLmD8XR0KBI2C4CLQ==', 
    'MD5OfBody': '8a38143c02186ec7aca7cc49fd68cf54', 
    'Body': '{image: image_path, image_name:hello_world}'
} 
S3 PUT RESPONSE
{
    'ResponseMetadata': {
        'RequestId': '59W202WKCNWRW2D4', 
        'HostId': 'jEp7QSN5lp/P5yaSL1A0NhMLAJ5RJgDgzY/5RDhcFdceoWzYRykTiTBGVf6QTOhQRXrL8SIdMNw=', 
        'HTTPStatusCode': 200, 
        'HTTPHeaders': {
            'x-amz-id-2': 'jEp7QSN5lp/P5yaSL1A0NhMLAJ5RJgDgzY/5RDhcFdceoWzYRykTiTBGVf6QTOhQRXrL8SIdMNw=', 
            'x-amz-request-id': '59W202WKCNWRW2D4', 
            'date': 'Sat, 18 Feb 2023 02:06:57 GMT', 
            'x-amz-version-id': '_Rn08ch5zSWHbFxT867.2tjqu_zJFWRD', 
            'x-amz-server-side-encryption': 'AES256', 
            'etag': '"89ff26fe1259ecc09f36e139af914c11"', 
            'server': 'AmazonS3', 
            'content-length': '0'
        }, 
        'RetryAttempts': 0
        }, 
    'ETag': '"89ff26fe1259ecc09f36e139af914c11"', 
    'ServerSideEncryption': 'AES256', 
    'VersionId': '_Rn08ch5zSWHbFxT867.2tjqu_zJFWRD'}
S3 GET RESPONSE


AWS CLI COMMANDS --> 

'''

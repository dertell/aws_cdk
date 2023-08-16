import boto3
from botocore.exceptions import ClientError
import logging
import os

def lambda_handler(event, context):

    tableName = os.environ.get("tableName")
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    labels = detect_labels(bucket, key)
    save_labels(labels, key, tableName)


def detect_labels(bucket, key):
    client = boto3.client('rekognition')
    try:
        response = client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key,
                }
            },
            MaxLabels=10
        )
    except ClientError as e:
        logging.error(e)

    labels = [label["Name"] for label in response["Labels"]]
    return labels
    
def save_labels(labels, key, tableName):
    client = boto3.client('dynamodb')
    try:
        response = client.put_item(
            TableName= tableName,
            Item={
                'Filename': {
                    'S': key
                },
                'Labels': {
                    'SS': labels
                }
            }
        )
    except ClientError as e:
        logging.error(e)


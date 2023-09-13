import boto3
from botocore.exceptions import ClientError
import logging
import os
import urllib.parse


rekognition = boto3.client('rekognition')
dynamo = boto3.client('dynamodb')


def lambda_handler(event, context):

    tableName = os.environ.get("tableName")
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    labels = detect_labels(bucket, key)
    save_labels(labels, key, tableName)


def detect_labels(bucket, key):
    try:
        response = rekognition.detect_labels(
            Image={
                'S3Object': {'Bucket': bucket,
                             'Name': key,
                             }},
            MaxLabels=10
        )
    except ClientError as e:
        logging.error(e)

    labels = {label["Name"]:{"S": str(round(label["Confidence"],2))+"%"} 
              for label in response["Labels"]}
    return labels


def save_labels(labels, key, tableName):
    sortkey = ""
    for label in list(labels.keys()):
        sortkey += label
    try:
        dynamo.put_item(TableName= tableName,
                        Item={'Filename': {'S': key},
                              'Sortkey': {'S': sortkey.lower()},
                              'Labels': {'M': labels}
                              })
    except ClientError as e:
        logging.error(e)

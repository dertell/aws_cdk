import boto3
from botocore.exceptions import ClientError
import os
import json

def main(event, context):
    try:
        search = event['queryStringParameters']['search']
        if search == "":
            return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "invalid query string"}),
        }
    except (KeyError, TypeError):
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "invalid query string"}),
        }
    client = boto3.client("dynamodb")
    try:
        response = client.scan(
            TableName = os.environ.get("tableName"),
            ExpressionAttributeValues = {":search": {"S": search}},
            ExpressionAttributeNames = {"#Sortkey": "Sortkey"},
            FilterExpression = "contains(#Sortkey, :search)",
            Limit = 20,
        )
    except ClientError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": [{"Key": "Something went wrong"}]}),
        }
    if response["Count"] == 0:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": [{"Key": "Sorry, I couldn't find that."}]}),
        }

    filenames = [r["Filename"]["S"] for r in response["Items"]]

    client = boto3.client("s3")
    result = []
    for file in filenames:
        data = {}
        try:
            link = client.generate_presigned_url('get_object', 
                                                 Params={'Bucket': os.environ.get('bucket'),
                                                         'Key': file}, ExpiresIn = 300)
            data["Key"] = file
            data["Link"] = link
            result.append(data)
        except ClientError:
            pass        
    return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": result},  indent=4),
        }


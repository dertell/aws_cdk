import boto3
from botocore.exceptions import ClientError
import os
import json

dynamo = boto3.client("dynamodb")

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
    try:
        response = dynamo.scan(
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
    result = [{ "Key": file,"Link":f"https://{os.environ.get('bucket')}.s3.eu-central-1.amazonaws.com/{file}"} for file in filenames]
    
    return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": result},  indent=4),
        }


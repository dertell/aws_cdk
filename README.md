
# AWS Rekognition CDK Python project!

This stack will create a S3 bucket, a DynamoDB Table and a lambda function.
When an object is placed inside the bucket the lambda function will use AWS
Rekognition to detect labels and make an etry with the filename and labels in
the DynamoDB Table.

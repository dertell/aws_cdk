from aws_cdk import (
    Stack,
)
from constructs import Construct
import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_lambda as lambda_


class MycdkStack(Stack):

    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        bucket = s3.Bucket(self, "MyfirstBucket", removal_policy=cdk.RemovalPolicy.DESTROY,
                           auto_delete_objects=True,
                           bucket_name="nf-rekognition-bucket")
        table = dynamodb.Table(self, "MyfirstTable", 
                               partition_key=dynamodb.Attribute(name="Filename", 
                                                                type=dynamodb.AttributeType.STRING),
                                table_name="nf-rekognition-table",
                                removal_policy=cdk.RemovalPolicy.DESTROY)
        function = lambda_.Function(self, "lambda-func", handler="lambda-func.lambda_handler",
                                    runtime=lambda_.Runtime.PYTHON_3_11,
                                    code=lambda_.Code.from_asset("./lambda"),
                                    function_name="nf-rekognition-function",
                                    retry_attempts=0)

        s3_event_source = cdk.aws_lambda_event_sources.S3EventSource(bucket, 
                                                                     events=[s3.EventType.OBJECT_CREATED_PUT])
        function.add_event_source(s3_event_source)
        function.add_to_role_policy(cdk.aws_iam.PolicyStatement(actions=["rekognition:*", "dynamodb:*",  "s3:*",
                "s3-object-lambda:*"], resources=["*"]))


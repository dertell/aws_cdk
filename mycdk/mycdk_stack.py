from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct
import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_dynamodb as dynamodb


class MycdkStack(Stack):

    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        bucket = s3.Bucket(self, "MyfirstBucket", removal_policy=cdk.RemovalPolicy.DESTROY,
                           auto_delete_objects=True,
                           bucket_name="nf-rekognition-bucket")
        table = dynamodb.Table(self, "MyfirstTable", 
                               partition_key=dynamodb.Attribute(name="Filename", 
                                                                type=dynamodb.AttributeType.STRING),
                                table_name="nf-rekognition-table")

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "MycdkQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

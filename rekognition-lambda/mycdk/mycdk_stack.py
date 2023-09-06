from aws_cdk import (
    Stack,
)
from constructs import Construct
import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_apigateway as apigateway
import aws_cdk.aws_ec2 as ec2
import os

class MycdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        bucket = s3.Bucket(self, "MyfirstBucket", removal_policy=cdk.RemovalPolicy.DESTROY,
                           auto_delete_objects=True,
                           bucket_name="nf-rekognition-bucket")
        

        table = dynamodb.Table(self, "MyfirstTable", 
                               partition_key=dynamodb.Attribute(name="Filename", 
                                                                type=dynamodb.AttributeType.STRING),
                                sort_key=dynamodb.Attribute(name="Sortkey", type=dynamodb.AttributeType.STRING),
                                table_name="nf-rekognition-table",
                                removal_policy=cdk.RemovalPolicy.DESTROY)
        

        function = lambda_.Function(self, "lambda-func", handler="lambda-func.lambda_handler",
                                    runtime=lambda_.Runtime.PYTHON_3_11,
                                    code=lambda_.Code.from_asset("./lambda"),
                                    function_name="nf-rekognition-function",
                                    retry_attempts=0,
                                    environment={"tableName": table.table_name})
        s3_event_source = cdk.aws_lambda_event_sources.S3EventSource(bucket, 
                                                                     events=[s3.EventType.OBJECT_CREATED_PUT])
        function.add_event_source(s3_event_source)
        function.add_to_role_policy(cdk.aws_iam.PolicyStatement(actions=["rekognition:*", "dynamodb:*",  "s3:*",
                "s3-object-lambda:*"], resources=["*"]))
        

        searchfunction = lambda_.Function(self, "search-lambda", handler="lambda-dydb.main",
                                          runtime=lambda_.Runtime.PYTHON_3_11,
                                          code=lambda_.Code.from_asset("./lambda"),
                                          function_name="search-function",
                                          retry_attempts=0,
                                          environment={"tableName": table.table_name,
                                                       "bucket": bucket.bucket_name})
        searchfunction.add_to_role_policy(cdk.aws_iam.PolicyStatement(actions=["dynamodb:*", "s3:*"],
                                                                      resources=["*"]))


        api = apigateway.LambdaRestApi(self, "myapi", handler=searchfunction, proxy=False, 
                                       api_key_source_type=apigateway.ApiKeySourceType.HEADER,
                                       deploy_options=apigateway.StageOptions(stage_name="neuefische"))
        resource = api.root.add_resource("images")
        resource.add_method("GET", api_key_required=True)
        
        plan = apigateway.UsagePlan(self, "myplan", name="myplan")
        plan.add_api_stage(stage=api.deployment_stage)

           
        instance = ec2.Instance(self, "Webapp", vpc=ec2.Vpc.from_lookup(self, "myvpc", 
                                                                        vpc_name="my-vpc"), 
                                instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, 
                                                                  ec2.InstanceSize.MICRO),
                                machine_image=ec2.MachineImage.lookup(name="traefik image", 
                                                                      owners=[os.environ.get("account")]),
                                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                                security_group=ec2.SecurityGroup.from_lookup_by_id(self, "seq", 
                                                                                   security_group_id="sg-0c043b656186408a9")
                                )
        instance.add_user_data(f'cd /home/ec2-user \n\
sudo sed -i "s/dashboard.voelsch.xyz/traefik.voelsch.xyz/" compose.yaml \n\
sudo sed -i "s/api.voelsch.xyz/flask.voelsch.xyz/" compose.yaml \n\
sudo sed -i "s/gjauaijw1d/{api.rest_api_id}/" compose.yaml \n\
sudo sed -i "s/ro99lo/{plan.usage_plan_id}/" compose.yaml \n\
sudo sed -i "s/https://gjauaijw1d.execute-api.eu-central-1.amazonaws.com/neuefische//{api.url}/" compose.yaml \n\
sudo systemctl start docker \n\
sudo docker-compose up')
        instance.add_to_role_policy(cdk.aws_iam.PolicyStatement(actions=["apigateway:*"], 
                                                                resources=["*"]))
        instance.node.add_dependency(api)
        instance.node.add_dependency(plan)
        cfneip = ec2.CfnEIPAssociation(self, "CfnEIP", allocation_id="eipalloc-0e8628d18580b5028",
                                       instance_id=instance.instance_id)




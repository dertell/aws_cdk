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
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_elasticloadbalancingv2 as lb
import os


bucketName = "new-nf-rekognition-bucket"
tableName = "new-nf-rekognition-table"

class MycdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        bucket = s3.Bucket(self, "MyfirstBucket", removal_policy=cdk.RemovalPolicy.DESTROY,
                           auto_delete_objects=True, block_public_access=s3.BlockPublicAccess(block_public_acls=False,block_public_policy=False,ignore_public_acls=False,restrict_public_buckets=False),
                           bucket_name=bucketName, object_ownership= s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,access_control=s3.BucketAccessControl.PUBLIC_READ)
        

        table = dynamodb.Table(self, "MyfirstTable", 
                               partition_key=dynamodb.Attribute(name="Filename", 
                                                                type=dynamodb.AttributeType.STRING),
                                sort_key=dynamodb.Attribute(name="Sortkey", type=dynamodb.AttributeType.STRING),
                                table_name=tableName,
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

        allow = ec2.SecurityGroup.from_lookup_by_id(self, "seq", security_group_id="sg-0c043b656186408a9")
        vpc=ec2.Vpc.from_lookup(self, "myvpc", vpc_name="my-vpc")

        cluster = ecs.Cluster(self, "mycluster", enable_fargate_capacity_providers=True,
                              vpc=vpc)
#        cluster = ecs.Cluster.from_cluster_attributes(self, "cluster", cluster_name="traefik", vpc=vpc)

        exe_role = cdk.aws_iam.Role.from_role_name(self, "exe_role", role_name="ecsTaskExecutionRole")
        task_role = cdk.aws_iam.Role.from_role_name(self, "task_role", role_name="apitaskrole")

        task_definition = ecs.FargateTaskDefinition(self, "TaskDef", execution_role=exe_role,
                                                    task_role=task_role, cpu=1024, memory_limit_mib=3072)
        task_definition.add_container("nf-traefik", image=ecs.ContainerImage.from_registry("docker.io/avoe/django:ecs7"),
                                      cpu=512,
                                      port_mappings=[ecs.PortMapping(container_port=80, host_port=80)],
                                      docker_labels={"traefik.enable":"true",
                                    "traefik.http.routers.dashboard.rule":os.environ.get("dashhost"),
                                    "traefik.http.routers.dashboard.service":"api@internal"})
                
        task_definition.add_container("nf-flask", image=ecs.ContainerImage.from_registry("docker.io/avoe/django:api.flask"),
                                      port_mappings=[ecs.PortMapping(container_port=5000, host_port=5000)], cpu=512,
                                      docker_labels={"traefik.enable":"true",
                                                     "traefik.http.routers.flask.rule":os.environ.get("apphost")},
                                      environment={"apiid": api.rest_api_id,
                                                   "usageplanid":plan.usage_plan_id,
                                                   "endpoint":api.url})

        service = ecs.FargateService(self, "Service", cluster=cluster, task_definition=task_definition,
                                     service_name="imagesearch", assign_public_ip=True,
                                     security_groups=[allow])
        
        target = lb.ApplicationTargetGroup.from_target_group_attributes(self, "target", target_group_arn="arn:aws:elasticloadbalancing:eu-central-1:738746962693:targetgroup/traefiktg/d0b74536f7961141")
        lbtarget = service.load_balancer_target(container_name="nf-traefik", container_port=80, protocol=ecs.Protocol.TCP)
        target.add_target(lbtarget)

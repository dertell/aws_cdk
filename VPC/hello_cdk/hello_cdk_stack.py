from aws_cdk import (
    Stack,
)
from constructs import Construct
import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_rds as rds
import aws_cdk.aws_autoscaling as autoscaling
import aws_cdk.aws_elasticloadbalancingv2 as elbv2
import aws_cdk.aws_sns as sns


class HelloCdkStack(Stack):

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

class ByeCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        vpc = ec2.Vpc(self, "TheVPC", ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
                      max_azs=2, subnet_configuration=[{"cidrMask": 24, "name":"public",
                                                        "subnetType": ec2.SubnetType.PUBLIC},
                                                       {"cidrMask": 24, "name":"private",
                                                        "subnetType": ec2.SubnetType.PRIVATE_ISOLATED}])


        bastionSG = ec2.SecurityGroup(self, "bastionSG", vpc=vpc)
        autoscalingSG = ec2.SecurityGroup(self, "autoscalingSG", vpc=vpc)
        albSG = ec2.SecurityGroup(self, "albSG", vpc=vpc)
        mysqlSG = ec2.SecurityGroup(self, "mysqlSG", vpc=vpc)

        bastionSG.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))
        autoscalingSG.add_ingress_rule(ec2.Peer.security_group_id(bastionSG.security_group_id), ec2.Port.tcp(22))
        autoscalingSG.add_ingress_rule(ec2.Peer.security_group_id(albSG.security_group_id), ec2.Port.tcp(80))
        albSG.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))
        albSG.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443))
        mysqlSG.add_ingress_rule(ec2.Peer.security_group_id(autoscalingSG.security_group_id), ec2.Port.tcp(3306))
        mysqlSG.add_ingress_rule(ec2.Peer.security_group_id(bastionSG.security_group_id), ec2.Port.tcp(3306))
        

        mysqlInstance = rds.DatabaseInstance(self, "mysqlInstnace", engine=rds.DatabaseInstanceEngine.MYSQL,
                                             vpc=vpc, instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2,
                                                                                        ec2.InstanceSize.MICRO), 
                                             security_groups=[mysqlSG], removal_policy=cdk.RemovalPolicy.DESTROY,
                                             allocated_storage=20, database_name="MyDB",
                                             vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
                                             credentials=rds.Credentials.from_password(username="admin",
                                                                                       password=cdk.SecretValue.unsafe_plain_text("password123")))
        endpoint = mysqlInstance.db_instance_endpoint_address


        bastionHost = ec2.Instance(self, "BastionHost", vpc=vpc, 
                                   instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
                                   machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023),
                                   security_group=bastionSG, vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC))
        

        template = ec2.LaunchTemplate(self,"LaunchTemplate", machine_image=ec2.MachineImage.latest_amazon_linux2023(),
                                      security_group=autoscalingSG, instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2,
                                                                                                      ec2.InstanceSize.MICRO),
                                      user_data=ec2.UserData.add_execute_file_command(self, file_path="./script/user-data.sh",
                                                                                      arguments=endpoint))
        

        topic = sns.Topic(self, "MyTopic")
        sns.Subscription(self, "Subscription", topic=topic, endpoint="example@email.com", protocol=sns.SubscriptionProtocol.EMAIL)


        autog = autoscaling.AutoScalingGroup(self, "ASG", vpc=vpc, launch_template=template, auto_scaling_group_name="MyASG",
                                             health_check=autoscaling.HealthCheck.elb(grace=cdk.Duration.minutes(5)),
                                             max_capacity=4, min_capacity=1,
                                             notifications=[autoscaling.NotificationConfiguration(topic=topic)])
        autog.scale_on_cpu_utilization("ASG", target_utilization_percent=75)


        lb = elbv2.ApplicationLoadBalancer(self, "LB", vpc=vpc, internet_facing=True, security_group=albSG)
        listener = lb.add_listener("Listener", port=80)
        listener.add_targets("Fleet", port=80, targets=[autog])
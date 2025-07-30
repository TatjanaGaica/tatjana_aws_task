from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_iam as iam,
    aws_logs as logs,
    RemovalPolicy,
    Tags,
    CfnOutput,
)
from constructs import Construct

class SageMakerAIStudioStack(Stack):
    """
    A foundational AWS CDK stack for SageMaker AI Studio infrastructure.
    This stack provisions a VPC, an S3 bucket for data, and an IAM role
    with permissions commonly required by SageMaker.
    """

    def __init__(self, scope: Construct, construct_id: str,
                 vpc_cidr: str = "10.0.0.0/16",
                 max_azs: int = 2,
                 bucket_name_prefix: str = "sagemaker-ai-studio-data",
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        flow_log_role = iam.Role(
            self, "VPCFlowLogRole",
            assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"),
            description="IAM role for VPC Flow Logs to CloudWatch Logs."
        )
        flow_log_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogGroups",
                    "logs:DescribeLogStreams"
                ],
                resources=["*"]
            )
        )

        flow_log_group = logs.LogGroup(
            self, "VPCFlowLogGroup",
            log_group_name=f"/aws/vpc/flow-logs/{self.stack_name}-VPC",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.vpc = ec2.Vpc(
            self, "SageMakerAIStudioVPC",
            max_azs=max_azs,
            ip_addresses=ec2.IpAddresses.cidr(vpc_cidr),
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=28
                )
            ],
            flow_logs={
                "S3FlowLogs": ec2.FlowLogOptions(
                    destination=ec2.FlowLogDestination.to_cloud_watch_logs(
                        flow_log_group,
                        flow_log_role
                    )
                )
            }
        )

        self.data_bucket = s3.Bucket(
            self, "SageMakerAIStudioDataBucket",
            bucket_name=f"{bucket_name_prefix}-{self.account}-{self.region}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        self.sagemaker_role = iam.Role(
            self, "SageMakerAIStudioExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            description="IAM role for SageMaker AI Studio execution.",
        )

        self.sagemaker_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
        )
        self.data_bucket.grant_read_write(self.sagemaker_role)

        self.sagemaker_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                ],
                resources=[f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/sagemaker/*"]
            )
        )
        self.sagemaker_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams"
                ],
                resources=[f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/sagemaker/*:log-stream:*"]
            )
        )

        CfnOutput(
            self, "SageMakerRoleArn",
            value=self.sagemaker_role.role_arn,
            description="ARN of the IAM role for SageMaker AI Studio."
        )
        CfnOutput(
            self, "SageMakerDataBucketName",
            value=self.data_bucket.bucket_name,
            description="Name of the S3 bucket for SageMaker AI Studio data."
        )
        CfnOutput(
            self, "SageMakerVpcId",
            value=self.vpc.vpc_id,
            description="ID of the VPC created for SageMaker AI Studio."
        )
        CfnOutput(
            self, "VPCFlowLogGroupName",
            value=flow_log_group.log_group_name,
            description="Name of the CloudWatch Log Group for VPC Flow Logs."
        )

        for i, subnet in enumerate(self.vpc.public_subnets):
            CfnOutput(self, f"PublicSubnetId{i}", value=subnet.subnet_id,
                      description=f"ID of Public Subnet {i}")
        for i, subnet in enumerate(self.vpc.private_subnets):
            CfnOutput(self, f"PrivateSubnetId{i}", value=subnet.subnet_id,
                      description=f"ID of Private Subnet {i}")

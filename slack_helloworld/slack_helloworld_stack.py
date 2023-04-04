import os

from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_certificatemanager as acm,
)
from aws_cdk.aws_apigateway import SecurityPolicy, EndpointType
from aws_cdk.aws_ecr import Repository

from constructs import Construct


class SlackHelloworldStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        image_tag = os.getenv("IMAGE_TAG", "latest")
        ecr_image = _lambda.DockerImageCode.from_ecr(
            repository=Repository.from_repository_name(self, "slack-helloworld-repo", "slack-helloworld"),
            tag_or_digest=image_tag
        )
        slack_helloworld_domain_name = "slack-helloworld.bullyrooks.com"
        # Create a certificate for the domain name
        slack_helloworld_certificate = acm.Certificate.from_certificate_arn(
            self, "hello-lambda_certificate", certificate_arn="arn:aws:acm:us-west-2:108452827623:certificate/c0f1a0ec-0566-449a-b0e5-217762f51b95")


        slack_lambda = _lambda.DockerImageFunction(
            scope=self,
            id="slack-helloworld-lambda",
            # Function name on AWS
            function_name="slack-helloworld",
            # Use aws_cdk.aws_lambda.DockerImageCode.from_image_asset to build
            # a docker image on deployment
            code=ecr_image,
        )

        ssm_policy_statement = iam.PolicyStatement(
            actions=["ssm:GetParameter"],
            resources=["arn:aws:ssm:us-west-2:108452827623:parameter/prod/chatai/*",
                       ],
            effect=iam.Effect.ALLOW
        )
        slack_lambda.role.add_to_policy(ssm_policy_statement)

        slack_helloworld_api = apigateway.LambdaRestApi(self, "slack-helloworld-api",
                                                        rest_api_name="Slack Helloworld Service",
                                                        description="Provides Slack Access",
                                                        handler=slack_lambda,
                                                        proxy=False,
                                                        )

        slack_helloworld_api.add_domain_name(
            id="slack-lambda-domain",
            domain_name=slack_helloworld_domain_name,
            certificate=slack_helloworld_certificate,
            security_policy=SecurityPolicy.TLS_1_2,
            endpoint_type=EndpointType.REGIONAL,
        )

        # Add a POST method for the Slack bot
        slack_resource = slack_helloworld_api.root.add_resource("slack")

        # slack_wildcard_resource = slack_resource.add_resource("{proxy+}")
        slack_resource.add_method("POST")

        # Create a deployment explicitly
        deployment = apigateway.Deployment(self, "Deployment",
                                      api=slack_helloworld_api)

        # Map the deployment to the root URL
        apigateway.Stage(self, "prod",
                    deployment=deployment,
                    stage_name="",
                    rest_api=slack_helloworld_api)
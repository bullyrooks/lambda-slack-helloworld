import os

from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway, )
from aws_cdk.aws_ecr import Repository
from constructs import Construct


class SlackHelloworldStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.build_lambda_func()

    def build_lambda_func(self):
        image_tag = os.getenv("IMAGE_TAG", "latest")
        ecr_image = _lambda.DockerImageCode.from_ecr(
            repository=Repository.from_repository_name(self, "slack-helloworld-repo", "slack-helloworld"),
            tag_or_digest=image_tag
        )
        prediction_lambda = _lambda.DockerImageFunction(
            scope=self,
            id="slack-helloworld-lambda",
            # Function name on AWS
            function_name="slack-helloworld",
            # Use aws_cdk.aws_lambda.DockerImageCode.from_image_asset to build
            # a docker image on deployment
            code=self.ecr_image,
        )

        slack_helloworld_api = apigateway.LambdaRestApi(self, "slack-helloworld-api",
                                                        rest_api_name="Slack Helloworld Service",
                                                        description="Provides Slack Access",
                                                        handler=prediction_lambda,
                                                        proxy=False)

        # Add a POST method for the Slack bot
        slack_resource = slack_helloworld_api.root.add_resource("slack")
        slack_resource.add_method("POST")

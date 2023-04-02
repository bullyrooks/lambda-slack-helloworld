import os

from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam,
)
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
            resources=["arn:aws:ssm:us-west-2:108452827623:parameter/prod/chatai/lambda.api.key",
                       "arn:aws:ssm:us-west-2:108452827623:parameter/prod/chatai/slack.app.token",
                       "arn:aws:ssm:us-west-2:108452827623:parameter/prod/chatai/slack.bot.token",
                       "arn:aws:ssm:us-west-2:108452827623:parameter/prod/chatai/slack.signing.secret",
                       ],
            effect=iam.Effect.ALLOW
        )
        slack_lambda.role.add_to_policy(ssm_policy_statement)

        slack_helloworld_api = apigateway.LambdaRestApi(self, "slack-helloworld-api",
                                                        rest_api_name="Slack Helloworld Service",
                                                        description="Provides Slack Access",
                                                        handler=slack_lambda,
                                                        proxy=False,
                                                        deploy_options=apigateway.StageOptions(stage_name="prod"),
                                                        )

        # Add a POST method for the Slack bot
        slack_resource = slack_helloworld_api.root.add_resource("slack")

        slack_wildcard_resource = slack_resource.add_resource("{proxy+}")
        slack_wildcard_resource.add_method("POST")

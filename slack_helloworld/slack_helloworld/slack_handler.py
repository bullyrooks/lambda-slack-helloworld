import os
import logging
import logging.config

import boto3
import requests
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)


ssm = boto3.client('ssm', region_name=os.environ["AWS_REGION"])
bottokenresponse = ssm.get_parameter(
    Name='/prod/chatai/slack.bot.token',
    WithDecryption=True
)
bot_token = bottokenresponse["Parameter"]["Value"]

signingsecretresponse = ssm.get_parameter(
    Name='/prod/chatai/slack.signing.secret',
    WithDecryption=True
)
signing_secret = signingsecretresponse["Parameter"]["Value"]

apikeyresponse = ssm.get_parameter(
    Name='/prod/chatai/lambda.api.key',
    WithDecryption=True
)
api_key = apikeyresponse["Parameter"]["Value"]

lambda_client = boto3.client('helloWorld-cdk', region_name=os.environ["AWS_REGION"])

# process_before_response must be True when running on FaaS
app = App(process_before_response=True,
          token=bot_token,
          logger=logger,
          signing_secret=signing_secret)

@app.command("/hello")
def respond_to_slack_within_3_seconds(ack, respond, command):
    logger.info("inside hello command")
    ack("Hi!")

    response = call_hello_world(api_key)
    logger.info("got a response back: %s", response)

    # Check the response and send a message to the channel
    if response['status'] == 200:
        response_text = response['body']['message']
    else:
        response_text = "An error occurred while calling the other Lambda function."

    respond({
        "response_type": "in_channel",
        "text": response_text
    })

def call_hello_world(api_key, ):
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
    }
    endpoint_url = 'https://08ejndnqjb.execute-api.us-west-2.amazonaws.com/prod'
    response = requests.get(endpoint_url, headers=headers)
    return response

def handler(event, context):
    logger.info("handling inbound event: %s", event)
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
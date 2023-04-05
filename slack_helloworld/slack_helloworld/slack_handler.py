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

apikeyresponse = ssm.get_parameter(
    Name='/prod/chatai/lambda.api.key',
    WithDecryption=True
)
api_key = apikeyresponse["Parameter"]["Value"]

helloworldurlresponse = ssm.get_parameter(
    Name='/prod/chatai/helloworld.api.url',
    WithDecryption=False
)
helloworld_url = helloworldurlresponse["Parameter"]["Value"]
chataiurlresponse = ssm.get_parameter(
    Name='/prod/chatai/chatai.api.url',
    WithDecryption=False
)
chatai_url = chataiurlresponse["Parameter"]["Value"]
chataiapikeyresponse = ssm.get_parameter(
    Name='/prod/chatai/chatai.api.key',
    WithDecryption=True
)
chatai_api_key = chataiapikeyresponse["Parameter"]["Value"]


# process_before_response must be True when running on FaaS
app = App(process_before_response=True,
          token=bot_token,
          logger=logger,
          signing_secret=signing_secret,
          )

@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    logger.info("inside handle_app_mentions: %s", body)
    response = call_chatai(body)
    say(response)

@app.command("/hello")
def respond_to_slack_within_3_seconds(ack, respond, command):
    logger.info("inside hello command")
    ack("Hi!")

    message, status_code = call_hello_world(api_key)
    logger.info("got a response back: %s, %s", status_code, message)

    # Check the response and send a message to the channel
    # Check the response and send a message to the channel
    if status_code == 200:
        response_text = message
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

    response = requests.get(helloworld_url, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        message = response_json["message"]
        return message, response.status_code
    else:
        return None, response.status_code

def call_chatai(text):
    headers = {
        'x-api-key': chatai_api_key,
        'Content-Type': 'application/json',
    }
    logger.info("chatai request: %s", text)
    response = requests.post(chatai_url,
                             json={"text": text},
                             headers=headers,
                             )
    logger.info("chatai response: %s", response)
    if response.status_code == 200:
        response_json = response.json()
        message = response_json["response"]
        return message, response.status_code
    else:
        return None, response.status_code

def handler(event, context):
    logger.info("handling inbound event: %s", event)
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
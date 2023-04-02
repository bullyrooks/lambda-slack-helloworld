import os
import logging
import logging.config

import boto3
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

# process_before_response must be True when running on FaaS
app = App(process_before_response=True, token=bot_token, logger=logger)

@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    logger.info(body)
    say("What's up?")

@app.command("/hello")
def respond_to_slack_within_3_seconds(ack):
    ack("Hi!")

def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
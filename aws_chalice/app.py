import json
import logging
import re

import boto3
from chalice import Chalice, Response
from slack_bolt import Ack, App, Say
from slack_bolt.adapter.aws_lambda.chalice_handler import ChaliceSlackRequestHandler
from slack_bolt.adapter.aws_lambda.lambda_s3_oauth_flow import LambdaS3OAuthFlow

# process_before_response must be True when running on FaaS
bolt_app = App(process_before_response=True, oauth_flow=LambdaS3OAuthFlow())


def handle_app_mentions(body: dict, say: Say, logger: logging.Logger) -> None:
    logger.info(f"Receive: {body}")
    event = body["event"]
    # channel = event["channel"]
    ts = event["ts"]

    # Exclude mention from the message
    mention_text = re.sub(r"<@.*?> ", "", event["text"])

    # Access to Amazon Bedrock
    bedrock_client = boto3.client("bedrock-runtime")

    prompt = f"\n\nHuman: {mention_text}\n\nAssistant:"

    bedrock_body = {
        "prompt": prompt,
        "max_tokens_to_sample": 1024,
        "temperature": 1.0,
        "top_p": 0.999,
    }

    model_id = "anthropic.claude-instant-v1"
    response = bedrock_client.invoke_model(
        body=json.dumps(bedrock_body),
        modelId=model_id,
        accept="application/json",
        contentType="application/json",
    )

    response_body = json.loads(response.get("body").read())
    reply = response_body.get("completion")

    # Reply to thread
    say(f"{reply}", thread_ts=ts)


def respond_to_slack_within_3_seconds(ack: Ack) -> None:
    ack()


bolt_app.event("app_mention")(
    ack=respond_to_slack_within_3_seconds, lazy=[handle_app_mentions]
)


ChaliceSlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

# Don't change this variable name "app"
app = Chalice(app_name="pro-odoroki-bot")
slack_handler = ChaliceSlackRequestHandler(app=bolt_app, chalice=app)


@app.route(
    "/slack/events",
    methods=["POST"],
    content_types=["application/x-www-form-urlencoded", "application/json"],
)
def events() -> Response:
    return slack_handler.handle(app.current_request)


@app.route("/slack/install", methods=["GET"])
def install() -> Response:
    return slack_handler.handle(app.current_request)


@app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_redirect() -> Response:
    return slack_handler.handle(app.current_request)


# configure aws credentials properly
# pip install -r requirements.txt
# cp -p .chalice/config.json.oauth .chalice/config.json
# # edit .chalice/config.json
# rm -rf vendor/latest_slack_bolt && cp -pr ../../src vendor/latest_slack_bolt
# chalice deploy

# for local dev
# chalice local --stage dev --port 3000

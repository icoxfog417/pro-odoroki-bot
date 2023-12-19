import logging
import re

import chalicelib.message_retriever as mr
import chalicelib.pro_odoroki_generator as pog
from chalice import Chalice, Response
from chalicelib.bedrock import Bedrock
from slack_bolt import Ack, App, Say
from slack_bolt.adapter.aws_lambda.chalice_handler import ChaliceSlackRequestHandler
from slack_bolt.adapter.aws_lambda.lambda_s3_oauth_flow import LambdaS3OAuthFlow

# process_before_response must be True when running on FaaS
bolt_app = App(process_before_response=True, oauth_flow=LambdaS3OAuthFlow())


def handle_app_mentions(body: dict, say: Say, logger: logging.Logger) -> None:
    logger.info(f"Mention Event: Receive mention: {body}")

    # Please refer the structure of body at the following document
    # https://api.slack.com/events/app_mention
    event = body["event"]
    # channel = event["channel"]
    ts = event["ts"]

    # Exclude mention from the message
    message = mr.exclude_mentions(event["text"])
    bedrock = Bedrock()
    reply = bedrock.ask_to_claude(message, version="2.1")

    # Reply to thread
    say(f"{reply}", thread_ts=ts)


def handle_app_message(message: dict, say: Say, logger: logging.Logger) -> None:
    logger.info(f"Message Event: Observed message: {message}")

    # Please refer the structure of message at the following document
    # https://api.slack.com/events/app_mention
    _message = mr.exclude_mentions(message["text"])
    ts = message["ts"]
    url_pattern = re.compile(r"https?://\S+")
    urls = re.findall(url_pattern, _message)
    if len(urls) > 0:
        logger.info(f"Message Event: Detect url {urls[0]} so use description.")
        _message = mr.retrieve_description(urls[0])
    else:
        logger.info("Message Event: Use message as text.")

    logger.info(f"Message Event: Create prompt based on {_message}.")
    prompt_body = pog.generate(_message)
    logger.info(f"Message Event: Prompt is {prompt_body}.")
    bedrock = Bedrock()
    reply = bedrock.ask_to_claude(prompt_body, instant=True)
    logger.info(f"Message Event: Generated response: {reply}")
    reply_dict = pog.retrieve(reply)
    say(f"{reply_dict.get('reaction')}", thread_ts=ts)


def respond_to_slack_within_3_seconds(ack: Ack) -> None:
    ack()


bolt_app.event("app_mention")(
    ack=respond_to_slack_within_3_seconds, lazy=[handle_app_mentions]
)

AI_KEYWORDS = [
    ":bulb:",
    "ChatGPT",
    "OpenAI",
    "Bedrock",
    "Amazon Q",
    "Gemini",
    "DeepMind",
]
bolt_app.message(keyword=re.compile("|".join(AI_KEYWORDS), flags=re.IGNORECASE))(
    ack=respond_to_slack_within_3_seconds, lazy=[handle_app_message]
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

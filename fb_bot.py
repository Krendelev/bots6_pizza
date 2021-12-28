import os
import logging

import requests
from dotenv import load_dotenv
from flask import Flask, request

import fb_ui

logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route("/", methods=["GET"])
def verify():
    if not (args := request.args.to_dict()):
        return "Hi there!", 200
    if args["hub.challenge"] and args["hub.mode"] == "subscribe":
        if args["hub.verify_token"] != os.environ["VERIFICATION_TOKEN"]:
            return "Verification token mismatch", 403
        return args["hub.challenge"], 200


@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    # print(data)
    try:
        messaging = data["entry"][0]["messaging"][0]
        if text := messaging["message"].get("text"):
            send_menu(messaging["sender"]["id"])
            # send_message(messaging["sender"]["id"], text)
    except LookupError:
        return "Bad Request", 400
    else:
        return "OK", 200


def send_menu(recipient_id):
    url = "https://graph.facebook.com/v2.6/me/messages"
    params = {"access_token": os.environ["PAGE_ACCESS_TOKEN"]}
    headers = {"Content-Type": "application/json"}
    payload = {"recipient": {"id": recipient_id}, "message": fb_ui.make_menu("main")}
    response = requests.post(url, params=params, headers=headers, json=payload)
    response.raise_for_status()


def send_message(recipient_id, message):
    url = "https://graph.facebook.com/v2.6/me/messages"
    params = {"access_token": os.environ["PAGE_ACCESS_TOKEN"]}
    headers = {"Content-Type": "application/json"}
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message}}
    response = requests.post(url, params=params, headers=headers, json=payload)
    response.raise_for_status()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    load_dotenv()
    app.run(debug=True)

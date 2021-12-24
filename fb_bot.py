import os
import logging

import requests
from dotenv import load_dotenv
from flask import Flask, request


logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route("/", methods=["GET"])
def verify():
    hub = request.args.get("hub")
    if hub.challenge and hub.mode == "subscribe":
        if hub.verify_token != os.environ["VERIFICATION_TOKEN"]:
            return "Verification token mismatch", 403
        return hub.challenge, 200
    return "Hello world", 200


@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"]["text"]
                    send_message(sender_id, message_text)
    return "ok", 200


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

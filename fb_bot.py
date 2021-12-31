import logging
import os
import re

import requests
from dotenv import load_dotenv
from flask import Flask, request

import fb_ui
import store

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
        user_id = messaging["sender"]["id"]
        if postback := messaging.get("postback"):
            handle_user_request(user_id, postback.get("payload"))
        elif messaging.get("message"):
            menu = fb_ui.make_menu("main")
            send_message(user_id, menu)
    except LookupError:
        return "Bad Request", 400
    else:
        return "OK", 200


def handle_user_request(user_id, request):
    pattern = re.compile(r"^[\da-f]{8}-(?:[\da-f]{4}-){3}[\da-f]{12}$")
    # while request:
    match request.split():
        case ["MENU", page] if page in ["main", "special", "satisfying", "hot"]:
            menu = fb_ui.make_menu(page)
            send_message(user_id, menu)
        case ["MENU", item]: # if item := pattern.fullmatch(request).group():
            store.add_to_cart(user_id, item, 1)
        case ["CART"]:
            cart = fb_ui.make_cart(user_id)
            send_message(user_id, cart)
        case ["CART", item]: # if item := pattern.fullmatch(request).group():
            store.remove_from_cart(user_id, item)
            cart = fb_ui.make_cart(user_id)
            send_message(user_id, cart)
        case ["CHECKOUT"]:
            ...


def send_message(user_id, message):
    url = "https://graph.facebook.com/v2.6/me/messages"
    params = {"access_token": os.environ["PAGE_ACCESS_TOKEN"]}
    headers = {"Content-Type": "application/json"}
    payload = {"recipient": {"id": user_id}, "message": message}
    response = requests.post(url, params=params, headers=headers, json=payload)
    response.raise_for_status()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    load_dotenv()
    app.run(debug=True)

# "message": {"text": message}
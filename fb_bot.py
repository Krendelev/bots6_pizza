import logging
import os

from dotenv import load_dotenv
from flask import Flask, request

import fb_ui
import fb_utils
import store

logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route("/", methods=["GET"])
def verify():
    if not (args := request.args.to_dict()):
        return "Nothing to see here", 200
    if args["hub.challenge"] and args["hub.mode"] == "subscribe":
        if args["hub.verify_token"] != os.environ["VERIFICATION_TOKEN"]:
            return "Verification token mismatch", 403
        return args["hub.challenge"], 200


@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        messaging = data["entry"][0]["messaging"][0]
        user_id = messaging["sender"]["id"]
        if postback := messaging.get("postback"):
            handle_user_request(user_id, postback.get("payload"))
        elif messaging.get("message"):
            page = fb_utils.get_page("main")
            fb_utils.send_message(user_id, page)
    except LookupError:
        return "Bad Request", 400
    else:
        return "OK", 200


def handle_user_request(user_id, request):
    match request.split("+"):
        case ["MENU", category]:
            page = fb_utils.get_page(category)
            fb_utils.send_message(user_id, page)

        case ["MENU", item_name, item_id]:
            store.add_to_cart(user_id, item_id)
            fb_utils.send_message(
                user_id, {"text": f"Пицца '{item_name}' добавлена в корзину"}
            )
        case ["CART"]:
            cart = fb_ui.make_cart(user_id)
            fb_utils.send_message(user_id, cart)

        case ["CART", action, item]:
            getattr(store, action)(user_id, item)
            cart = fb_ui.make_cart(user_id)
            fb_utils.send_message(user_id, cart)


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    app.run(debug=True)

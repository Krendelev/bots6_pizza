import json

import fb_utils
import store
from fb_ui_data import CATEGORIES, CATEGORIES_CARD, SHOP_CARD, cart_card


def make_page(category):
    elements = [
        {
            "title": f"{p['name']} (₽{p['price'][0]['amount']})",
            "subtitle": p["description"],
            "image_url": store.get_file_link(
                p["relationships"]["main_image"]["data"]["id"]
            ),
            "buttons": [
                {
                    "type": "postback",
                    "title": "Добавить в корзину",
                    "payload": f"MENU+{p['name']}+{p['id']}",
                }
            ],
        }
        for p in fb_utils.get_products_by_category(category)
    ]
    return compose_message(SHOP_CARD, *elements, CATEGORIES_CARD)


def make_menu():
    return {
        category: json.dumps(make_page(category), ensure_ascii=False)
        for category in CATEGORIES
    }


def make_subtitle_for_cart(item):
    price = item["meta"]["display_price"]["with_tax"]["unit"]["formatted"]
    value = item["meta"]["display_price"]["with_tax"]["value"]["formatted"]
    qty = item["quantity"]
    return f"Цена: ₽{price}\nВ корзине: {qty} на сумму ₽{value}"


def make_cart(user_id):
    cart = store.get_cart_items(user_id)
    if not cart["data"]:
        return {"text": "Ваша корзина пуста"}

    total = cart["meta"]["display_price"]["with_tax"]["formatted"]
    cart_card["subtitle"] = f"Ваш заказ на сумму ₽{total}"

    elements = [
        {
            "title": p["name"],
            "subtitle": make_subtitle_for_cart(p),
            "image_url": p["image"]["href"],
            "buttons": [
                {
                    "type": "postback",
                    "title": "Добавить ещё одну",
                    "payload": f"CART+add_to_cart+{p['product_id']}",
                },
                {
                    "type": "postback",
                    "title": "Удалить из корзины",
                    "payload": f"CART+remove_from_cart+{p['id']}",
                },
            ],
        }
        for p in cart["data"]
    ]
    return compose_message(cart_card, *elements)


def compose_message(*elements):
    return {
        "attachment": {
            "type": "template",
            "payload": {"template_type": "generic", "elements": elements},
        }
    }

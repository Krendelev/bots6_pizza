from dotenv import load_dotenv

import fb_utils
import store

SHOP = {
    "title": "PIZZERIA",
    "image_url": "https://bit.ly/3z3gr4O",
    "subtitle": "Лучшая пицца для вас!",
    "buttons": [
        {"type": "postback", "title": "Корзина", "payload": "CART"},
        {"type": "postback", "title": "Оформить заказ", "payload": "CHECKOUT"},
    ],
}
CATEGORIES = {
    "title": "Не нашли пиццу по вкусу?",
    "image_url": "https://bit.ly/33Wecoh",
    "subtitle": "Посмотрите в разделах ниже",
    "buttons": [
        {"type": "postback", "title": "Особые", "payload": "MENU special"},
        {"type": "postback", "title": "Сытные", "payload": "MENU satisfying"},
        {"type": "postback", "title": "Острые", "payload": "MENU hot"},
    ],
}
CART = {
    "title": "Корзина",
    "image_url": "https://bit.ly/3EHxxpY",
    "buttons": [
        {"type": "postback", "title": "Доставить", "payload": "deliver"},
        {"type": "postback", "title": "Самовывоз", "payload": "pickup"},
        {"type": "postback", "title": "Меню", "payload": "MENU main"},
    ],
}


def make_menu(category):
    elements = []
    for p in fb_utils.get_products_by_category(category):
        image_url = store.get_file_link(p["relationships"]["main_image"]["data"]["id"])
        elements.append(
            {
                "title": f'{p["name"]} (₽{p["price"][0]["amount"]})',
                "image_url": image_url,
                "subtitle": p["description"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Добавить в корзину",
                        "payload": f"MENU {p['id']}",
                    }
                ],
            }
        )

    elements.append(CATEGORIES)
    elements.append(SHOP)

    return {
        "attachment": {
            "type": "template",
            "payload": {"template_type": "generic", "elements": elements},
        }
    }


def make_cart(user_id):
    cart = store.get_cart_items(user_id)
    if not cart["data"]:
        return {"text": "Ваша корзина пуста"}

    elements = []
    card = CART.copy()
    total = cart["meta"]["display_price"]["with_tax"]["formatted"]
    card["subtitle"] = f"Ваш заказ на сумму ₽{total}"
    elements.append(card)
    for p in cart["data"]:
        price = p["meta"]["display_price"]["with_tax"]["unit"]["formatted"]
        val = p["meta"]["display_price"]["with_tax"]["value"]["formatted"]
        descr = f"Цена: ₽{price}\nВ корзине: {p['quantity']} на сумму ₽{val}"
        elements.append(
            {
                "title": p["name"],
                "image_url": p["image"]["href"],
                "subtitle": descr,
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Добавить ещё одну",
                        "payload": f"MENU {p['product_id']}",
                    },
                    {
                        "type": "postback",
                        "title": "Удалить из корзины",
                        "payload": f"CART {p['id']}",
                    },
                ],
            }
        )
    return {
        "attachment": {
            "type": "template",
            "payload": {"template_type": "generic", "elements": elements},
        }
    }


if __name__ == "__main__":
    load_dotenv()

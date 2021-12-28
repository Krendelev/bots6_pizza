from dotenv import load_dotenv

import fb_utils
import store


def make_menu(category):
    elements = [
        {
            "title": f'{p["name"]} (₽{p["price"][0]["amount"]})',
            "image_url": store.get_file_link(
                p["relationships"]["main_image"]["data"]["id"]
            ),
            "subtitle": p["description"],
            "buttons": [
                {"type": "postback", "title": "Добавить в корзину", "payload": p["id"]},
            ],
        }
        for p in fb_utils.get_products_by_category(category)
    ]
    elements.append(
        {
            "title": "Не нашли пиццу по вкусу?",
            "image_url": "https://bit.ly/33Wecoh",
            "subtitle": "Посмотрите в разделах ниже",
            "buttons": [
                {"type": "postback", "title": "Особые", "payload": "special"},
                {"type": "postback", "title": "Сытные", "payload": "satisfying"},
                {"type": "postback", "title": "Острые", "payload": "hot"},
            ],
        }
    )
    elements.append(
        {
            "title": "PIZZERIA",
            "image_url": "https://bit.ly/3z3gr4O",
            "subtitle": "Лучшая пицца для вас!",
            "buttons": [
                {"type": "postback", "title": "Корзина", "payload": "CART"},
                {"type": "postback", "title": "Оформить заказ", "payload": "CHECKOUT"},
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

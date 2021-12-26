import json

from dotenv import load_dotenv

import store


def get_products():
    with open("_workfiles/products.json") as prod:
        return json.load(prod)[:5]


def make_menu():
    elements = [
        {
            "title": f'{p["name"]} (₽{p["price"][0]["amount"]})',
            "image_url": store.get_file_link(
                p["relationships"]["main_image"]["data"]["id"]
            ),
            "subtitle": p["description"],
            "buttons": [
                {
                    "type": "postback",
                    "title": "Добавить в корзину",
                    "payload": p["id"],
                },
            ],
        }
        for p in get_products()
    ]

    return {
        "attachment": {
            "type": "template",
            "payload": {"template_type": "generic", "elements": elements},
        }
    }


if __name__ == "__main__":
    load_dotenv()

    print(make_menu())

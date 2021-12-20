import json
import os
from dataclasses import asdict

from dotenv import load_dotenv

import pizzeria
import store


def fill_catalogue(product_list):
    with open(product_list) as pl:
        products = json.load(pl)

    for product in products:
        pizza = pizzeria.Pizza(
            product["name"],
            "",
            str(product["id"]),
            product["description"],
            product["product_image"]["url"],
            product["price"],
        )
        product_id = store.create_product(asdict(pizza))
        picture_id = store.create_file(pizza.image)
        store.set_main_image(product_id, picture_id)


def create_fields(flow_id, fields):
    for field in fields:
        instance = field(flow_id)
        store.create_field(asdict(instance))


def create_entries(shop_list):
    with open(shop_list) as sl:
        shops = json.load(sl)

    flow_slug = pizzeria.PizzeriaFlow().slug
    for shop in shops:
        pizzashop = pizzeria.Pizzeria(
            shop["address"]["full"],
            shop["alias"],
            shop["coordinates"]["lat"],
            shop["coordinates"]["lon"],
            os.environ["TELEGRAM_ID"],  # TODO: replace in production
        )
        store.create_entry(flow_slug, asdict(pizzashop))


if __name__ == "__main__":
    load_dotenv()

    fill_catalogue(os.path.join("data", "menu.json"))

    pizza_shop = store.create_flow(asdict(pizzeria.PizzeriaFlow()))
    fields = [
        pizzeria.Address,
        pizzeria.Alias,
        pizzeria.Latitude,
        pizzeria.Longitude,
        pizzeria.TelegramId,
    ]
    create_fields(pizza_shop, fields)
    create_entries(os.path.join("data", "addresses.json"))

    location = store.create_flow(asdict(pizzeria.CustomerLocationFlow()))
    fields = [pizzeria.Address, pizzeria.Latitude, pizzeria.Longitude]
    create_fields(location, fields)

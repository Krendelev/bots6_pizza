from itertools import zip_longest

import iuliia
from telegram import InlineKeyboardButton

import store


# https://docs.python.org/3/library/itertools.html
def grouper(iterable, n, fillvalue=None):
    "Collect data into non-overlapping fixed-length chunks or blocks"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def make_menu():
    items_per_page = 7
    products = {p["name"]: p["id"] for p in store.get_products()}
    buttons = (
        [InlineKeyboardButton(item, callback_data=products[item])] for item in products
    )
    menu = [list(filter(None, item)) for item in grouper(buttons, items_per_page)]
    back = InlineKeyboardButton("Назад", callback_data=-1)
    forward = InlineKeyboardButton("Показать ещё", callback_data=1)
    for page in menu[1:-1]:
        page.append([back, forward])
    menu[0].append([forward])
    menu[-1].append([back])
    return menu


def make_slug(text):
    slug = "-".join(text.lower().split())
    return iuliia.translate(slug, schema=iuliia.WIKIPEDIA)


def make_cart(cart):
    if not cart["data"]:
        return "Ваша корзина пуста"

    products = []
    for item in cart["data"]:
        name = item["name"]
        descr = item["description"]
        qty = item["quantity"]
        price = item["meta"]["display_price"]["with_tax"]["unit"]["formatted"]
        val = item["meta"]["display_price"]["with_tax"]["value"]["formatted"]
        products.append(
            f"*{name}*\n_{descr}_\nЦена: *{price}* рублей\nВ корзине: *{qty}* на сумму *{val}* рублей"
        )
    products.append(
        f'К оплате: *{cart["meta"]["display_price"]["with_tax"]["formatted"]}* рублей'
    )
    return "\n\n".join(products)


def make_order(cart, delivery):
    items = []
    for item in cart["data"]:
        value = item["meta"]["display_price"]["with_tax"]["value"]["formatted"]
        items.append(f"{item['name']} x {item['quantity']} = {value} рублей")

    total = cart["meta"]["display_price"]["with_tax"]["formatted"].replace(",", "_")

    items.append(f"Доставка: {delivery.cost} рублей")
    items.append(f"Итого: {int(total) + delivery.cost} рублей")
    items.append(f"Доставить по адресу: {delivery.address}")

    return "\n".join(items)


def make_order_description(cart):
    items = [f"{item['name']} – {item['quantity']}" for item in cart["data"]]
    return ", ".join(items)

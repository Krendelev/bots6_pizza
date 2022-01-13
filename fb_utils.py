import json
import os

import redis
import requests

import store

db = redis.Redis(
    host=os.getenv("REDIS_ENDPOINT"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASSWORD"),
)


def get_products_by_category(category):
    products = store.get_products()
    product_ids_by_category = {
        c["slug"]: [p["id"] for p in c["relationships"]["products"]["data"]]
        for c in store.get_categories()
    }
    return [p for p in products if p["id"] in product_ids_by_category[category]]


def get_menu_page(category):
    return json.loads(db.hget("menu", category).decode())


def send_message(user_id, message):
    url = "https://graph.facebook.com/v2.6/me/messages"
    params = {"access_token": os.environ["PAGE_ACCESS_TOKEN"]}
    headers = {"Content-Type": "application/json"}
    payload = {"recipient": {"id": user_id}, "message": message}
    response = requests.post(url, params=params, headers=headers, json=payload)
    response.raise_for_status()

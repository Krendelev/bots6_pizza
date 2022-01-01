import json
import hashlib
import os

import redis
from dotenv import load_dotenv

import store
import fb_ui


def main(db):
    products = store.get_products()
    new_hash = hashlib.md5(str(products).encode()).hexdigest()
    if new_hash != db.hget("menu", "hash").decode():
        db.hmset("menu", {"hash": new_hash, **fb_ui.make_menu()})
        return "Menu updated"
    return "Nothing to update"


if __name__ == "__main__":
    load_dotenv()

    db = redis.Redis(
        host=os.getenv("REDIS_ENDPOINT"),
        port=os.getenv("REDIS_PORT"),
        password=os.getenv("REDIS_PASSWORD"),
    )
    print(main(db))
    # with open("_workfiles/products.json") as prod:
    #     pr = json.load(prod)[0]

    # pj = json.dumps(pr, ensure_ascii=False).encode()
    # ph = hash(pj)
    # db.hmset("menu", {"hash": ph, "content": pj})
    # print(json.loads(db.hget("menu", "content").decode()))

import hashlib
import os

import redis
from dotenv import load_dotenv

import store
import fb_ui


def main():
    load_dotenv()
    db = redis.Redis(
        host=os.getenv("REDIS_ENDPOINT"),
        port=os.getenv("REDIS_PORT"),
        password=os.getenv("REDIS_PASSWORD"),
    )
    products = store.get_products()
    new_hash = hashlib.md5(str(products).encode()).hexdigest()
    if new_hash != db.hget("menu", "hash").decode():
        db.hmset("menu", {"hash": new_hash, **fb_ui.make_menu()})


if __name__ == "__main__":
    main()

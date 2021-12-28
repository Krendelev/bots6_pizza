import json

from dotenv import load_dotenv

import store


def get_products():
    with open("_workfiles/products.json") as prod:
        return json.load(prod)


def get_products_by_category(category_slug):
    products = get_products()
    product_ids_by_category = {
        c["slug"]: [p["id"] for p in c["relationships"]["products"]["data"]]
        for c in store.get_categories()
    }
    return [p for p in products if p["id"] in product_ids_by_category[category_slug]]


if __name__ == "__main__":
    load_dotenv()

    print(get_products_by_category("main"))

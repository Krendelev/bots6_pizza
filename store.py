import os
import time
from dotenv.main import load_dotenv

import requests
from dotenv import dotenv_values

BASE_URL = dotenv_values(".env").get("BASE_URL")


def get_access_token():
    expires = int(os.getenv("EXPIRES", 0))

    if expires <= int(time.time()):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "client_id": os.environ["CLIENT_ID"],
            "client_secret": os.environ["CLIENT_SECRET"],
            "grant_type": "client_credentials",
        }
        response = requests.post(os.environ["AUTH_URL"], headers=headers, data=payload)
        response.raise_for_status()
        content = response.json()
        os.environ["ACCESS_TOKEN"] = content["access_token"]
        os.environ["EXPIRES"] = str(content["expires"])
    return os.environ["ACCESS_TOKEN"]


def get_headers():
    access_token = get_access_token()
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def create_product(product):
    payload = {"type": "product", "status": "live", **product}
    response = requests.post(
        f"{BASE_URL}/products", headers=get_headers(), json={"data": payload}
    )
    response.raise_for_status()
    return response.json()["data"]["id"]


def set_main_image(product_id, image_id):
    payload = {"type": "main_image", "id": image_id}
    response = requests.post(
        f"{BASE_URL}/products/{product_id}/relationships/main-image",
        headers=get_headers(),
        json={"data": payload},
    )
    response.raise_for_status()


def get_products():
    response = requests.get(f"{BASE_URL}/products", headers=get_headers())
    response.raise_for_status()
    return response.json()["data"]


def get_product(item_id):
    response = requests.get(f"{BASE_URL}/products/{item_id}", headers=get_headers())
    response.raise_for_status()
    return response.json()["data"]


def get_categories():
    response = requests.get(f"{BASE_URL}/categories", headers=get_headers())
    response.raise_for_status()
    return response.json()["data"]


def get_cart(cart_id):
    response = requests.get(f"{BASE_URL}/carts/{cart_id}", headers=get_headers())
    response.raise_for_status()
    return response.json()


def delete_cart(cart_id):
    response = requests.delete(f"{BASE_URL}/carts/{cart_id}", headers=get_headers())
    response.raise_for_status()


def add_to_cart(cart, item_id, quantity):
    headers = {**get_headers(), "X-MOLTIN-CURRENCY": "RUB"}
    payload = {"id": item_id, "type": "cart_item", "quantity": int(quantity)}
    response = requests.post(
        f"{BASE_URL}/carts/{cart}/items", headers=headers, json={"data": payload}
    )
    response.raise_for_status()


def update_cart_item(cart, item_id, quantity):
    payload = {"quantity": int(quantity)}
    response = requests.put(
        f"{BASE_URL}/carts/{cart}/items/{item_id}",
        headers=get_headers(),
        json={"data": payload},
    )
    response.raise_for_status()


def remove_from_cart(cart, item_id):
    response = requests.delete(
        f"{BASE_URL}/carts/{cart}/items/{item_id}", headers=get_headers()
    )
    response.raise_for_status()


def get_cart_items(cart):
    response = requests.get(f"{BASE_URL}/carts/{cart}/items", headers=get_headers())
    response.raise_for_status()
    return response.json()


def create_file(file_location):
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    files = {"file_location": (None, file_location)}
    response = requests.post(f"{BASE_URL}/files", headers=headers, files=files)
    response.raise_for_status()
    return response.json()["data"]["id"]


def get_file_link(file_id):
    response = requests.get(f"{BASE_URL}/files/{file_id}", headers=get_headers())
    response.raise_for_status()
    return response.json()["data"]["link"]["href"]


def create_customer(name, email):
    payload = {"type": "customer", "name": name, "email": email}
    response = requests.post(
        f"{BASE_URL}/customers", headers=get_headers(), json={"data": payload}
    )
    response.raise_for_status()
    return response.json()["data"]["id"]


def find_customer(email):
    payload = {"filter": f"eq(email,{email})"}
    response = requests.get(
        f"{BASE_URL}/customers", headers=get_headers(), params=payload
    )
    response.raise_for_status()
    return response.json()["data"]


def get_customers():
    response = requests.get(f"{BASE_URL}/customers", headers=get_headers())
    response.raise_for_status()
    return response.json()["data"]


def create_flow(entity):
    payload = {"type": "flow", "enabled": True, **entity}
    response = requests.post(
        f"{BASE_URL}/flows", headers=get_headers(), json={"data": payload}
    )
    response.raise_for_status()
    return response.json()["data"]["id"]


def create_field(field):
    payload = {"type": "field", "required": True, "enabled": True, **field}
    response = requests.post(
        f"{BASE_URL}/fields", headers=get_headers(), json={"data": payload}
    )
    response.raise_for_status()


def create_entry(flow_slug, entry):
    payload = {"type": "entry", **entry}
    response = requests.post(
        f"{BASE_URL}/flows/{flow_slug}/entries",
        headers=get_headers(),
        json={"data": payload},
    )
    response.raise_for_status()
    return response.json()["data"]["id"]


def update_entry(flow_slug, entry_id, field_slug, value):
    payload = {
        "type": "entry",
        "id": entry_id,
        field_slug: value,
    }
    response = requests.put(
        f"{BASE_URL}/flows/{flow_slug}/entries/{entry_id}",
        headers=get_headers(),
        json={"data": payload},
    )
    response.raise_for_status()


def get_entries(slug):
    response = requests.get(f"{BASE_URL}/flows/{slug}/entries", headers=get_headers())
    response.raise_for_status()
    return response.json()["data"]


def get_entry(slug, entry_id):
    response = requests.get(
        f"{BASE_URL}/flows/{slug}/entries/{entry_id}", headers=get_headers()
    )
    response.raise_for_status()
    return response.json()["data"]


def delete_entry(slug, entry_id):
    response = requests.delete(
        f"{BASE_URL}/flows/{slug}/entries/{entry_id}", headers=get_headers()
    )
    response.raise_for_status()


if __name__ == "__main__":
    load_dotenv()
    print(get_products()[0])

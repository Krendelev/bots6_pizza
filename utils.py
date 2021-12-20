import os
from dataclasses import asdict

from dotenv import load_dotenv
from geopy import distance, geocoders

import pizzeria
import store


def get_product(product_id):
    product = store.get_product(product_id)
    image = store.get_file_link(product["relationships"]["main_image"]["data"]["id"])
    return pizzeria.Product(
        product["name"], product["description"], product["price"][0]["amount"], image
    )


def get_coordinates(address):
    coder = geocoders.Yandex(os.environ["GEOCODER_API_KEY"])
    return coder.geocode(address, exactly_one=True)


def get_address(location):
    coder = geocoders.Yandex(os.environ["GEOCODER_API_KEY"])
    place = coder.reverse(f"{location.latitude}, {location.longitude}")
    return place.address


def get_distance(entry):
    return entry["distance"]


def get_customer_location(message):
    if location := message.location:
        address = get_address(location)
    elif (location := get_coordinates(message.text)) is None:
        return None

    address = message.text or address
    return pizzeria.CustomerLocation(address, location.latitude, location.longitude)


def save_customer_location(location):
    slug = pizzeria.CustomerLocationFlow().slug
    return store.create_entry(slug, asdict(location))


def get_delivery_info(location):
    slug = pizzeria.PizzeriaFlow().slug
    entries = store.get_entries(slug)
    for entry in entries:
        entry["distance"] = distance.distance(
            (location.latitude, location.longitude),
            (entry["latitude"], entry["longitude"]),
        ).km
    closest_shop = min(entries, key=get_distance)
    return pizzeria.DeliveryInfo(
        location.address,
        location.latitude,
        location.longitude,
        closest_shop["telegram-id"],
        closest_shop["address"],
        closest_shop["distance"],
    )


def cleanup_locations():
    slug = pizzeria.CustomerLocationFlow().slug
    entries = store.get_entries(slug)
    for entry in entries:
        store.delete_entry(slug, entry["id"])


if __name__ == "__main__":
    load_dotenv()

    cleanup_locations()

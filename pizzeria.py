from dataclasses import InitVar, dataclass, field

import ui


@dataclass
class Pizza:
    name: str
    slug: str
    sku: str
    description: str
    image: str
    price_amount: InitVar[int]
    price: list = field(default_factory=list)
    manage_stock: bool = False
    commodity_type: str = "physical"

    def __post_init__(self, price_amount):
        self.slug = ui.make_slug(self.name)
        self.price.append(
            {"amount": price_amount, "currency": "RUB", "includes_tax": True}
        )


@dataclass
class Pizzeria:
    address: str
    alias: str
    latitude: float
    longitude: float
    telegram_id: int


@dataclass
class PizzeriaFlow:
    name: str = "Pizzeria"
    slug: str = "pizzeria"
    description: str = "Represents a pizzeria object"


@dataclass
class Field:
    flow_id: InitVar[str]
    relationships: dict = field(default_factory=dict)

    def __post_init__(self, flow_id):
        self.relationships = {"flow": {"data": {"type": "flow", "id": flow_id}}}


@dataclass
class Address(Field):
    name: str = "Address"
    slug: str = "address"
    field_type: str = "string"
    description: str = "Location full address"
    order: int = 1


@dataclass
class Alias(Field):
    name: str = "Alias"
    slug: str = "alias"
    field_type: str = "string"
    description: str = "Location alias"
    order: int = 2


@dataclass
class Latitude(Field):
    name: str = "Latitude"
    slug: str = "latitude"
    field_type: str = "float"
    description: str = "Location latitude"
    order: int = 3


@dataclass
class Longitude(Field):
    name: str = "Longitude"
    slug: str = "longitude"
    field_type: str = "float"
    description: str = "Location longitude"
    order: int = 4


@dataclass
class TelegramId(Field):
    name: str = "Telegram id"
    slug: str = "telegram-id"
    field_type: str = "integer"
    description: str = "Contractor's telegram id"
    order: int = 5


@dataclass
class CustomerLocationFlow:
    name: str = "Customer location"
    slug: str = "customer-location"
    description: str = "Represents a customer location object"


@dataclass
class CustomerLocation:
    address: str
    latitude: float
    longitude: float


@dataclass
class Product:
    name: str
    description: str
    price: int
    image: str
    caption: str = ""

    def __post_init__(self):
        self.caption = (
            f"*{self.name}*\nЦена: {self.price} рублей\n\n_{self.description}_"
        )


@dataclass
class DeliveryInfo:
    address: str
    latitude: float
    longitude: float
    deliveryman: int
    shop: str
    distance: float
    cost: int = 0
    message: str = ""

    def __post_init__(self):
        delivery_price = {0.5: 0, 5: 100, 20: 300}
        for boundary, price in delivery_price.items():
            if self.distance <= boundary:
                self.cost = price
                break
        else:
            self.cost = None

        msg = f"Ближайшая к вам пиццерия находится по адресу:\n{self.shop}\n"
        if self.cost == 0:
            self.message = f"{msg}Мы можем доставить ваш заказ бесплатно."
        elif self.cost is None:
            self.message = (
                f"{msg}К сожалению, мы не можем доставить заказ по вашему адресу."
            )
        else:
            self.message = f"{msg}Доставка будет стоить {self.cost} рублей."

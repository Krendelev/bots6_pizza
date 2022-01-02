CATEGORIES = ["main", "special", "satisfying", "hot"]
SHOP_CARD = {
    "title": "PIZZERIA",
    "subtitle": "Лучшая пицца для вас!",
    "image_url": "https://bit.ly/3z3gr4O",
    "buttons": [
        {"type": "postback", "title": "Корзина", "payload": "CART"},
        {"type": "postback", "title": "Акции", "payload": "PROMOTIONS"},
        {"type": "postback", "title": "Оформить заказ", "payload": "CHECKOUT"},
    ],
}
CATEGORIES_CARD = {
    "title": "Не нашли пиццу по вкусу?",
    "subtitle": "Посмотрите в разделах ниже",
    "image_url": "https://bit.ly/33Wecoh",
    "buttons": [
        {"type": "postback", "title": "Особые", "payload": "MENU+special"},
        {"type": "postback", "title": "Сытные", "payload": "MENU+satisfying"},
        {"type": "postback", "title": "Острые", "payload": "MENU+hot"},
    ],
}
cart_card = {
    "title": "Корзина",
    "image_url": "https://bit.ly/3EHxxpY",
    "buttons": [
        {"type": "postback", "title": "Доставить", "payload": "deliver"},
        {"type": "postback", "title": "Самовывоз", "payload": "pickup"},
        {"type": "postback", "title": "Меню", "payload": "MENU+main"},
    ],
}

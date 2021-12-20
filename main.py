import logging
import os
import time

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    LabeledPrice,
    ParseMode,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    PreCheckoutQueryHandler,
    Updater,
)

import ui
import store
import utils

logger = logging.getLogger(__name__)

MENU, PRODUCT, CART, CHECKOUT, PAYMENT = "@0 @1 @2 @3 @4".split()
DELIVERY_RANGE = 20
CHECK_AFTER = 3600


def start(update, context):
    context.chat_data["curr_page"] = 0
    return show_menu(update, context)


def show_menu(update, context):
    if query := update.callback_query:
        query.answer()
        if query.data != MENU:
            context.chat_data["curr_page"] += int(query.data)

    keyboard = context.bot_data["menu"][context.chat_data["curr_page"]]
    reply_markup = InlineKeyboardMarkup(
        keyboard + [[InlineKeyboardButton("Корзина", callback_data=CART)]]
    )
    update.effective_message.reply_text(
        "Выберите вашу пиццу:", reply_markup=reply_markup
    )
    update.effective_message.delete()
    return MENU


def show_product(update, context):
    query = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton("Добавить в корзину", callback_data=query.data)],
        [
            InlineKeyboardButton("Меню", callback_data=MENU),
            InlineKeyboardButton("Корзина", callback_data=CART),
        ],
    ]
    product = utils.get_product(query.data)
    update.effective_message.reply_photo(
        product.image,
        caption=product.caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    update.effective_message.delete()
    return PRODUCT


def add_to_cart(update, context):
    query = update.callback_query
    query.answer("Пицца добавлена в корзину")
    store.add_to_cart(update.effective_user.id, query.data, 1)
    return PRODUCT


def show_cart(update, context):
    cart = store.get_cart_items(update.effective_user.id)
    order = ui.make_cart(cart)
    keyboard = [
        [
            InlineKeyboardButton(
                f'Удалить {p["name"]}', callback_data=f'{p["id"]} {p["quantity"]}'
            )
        ]
        for p in cart["data"]
    ]
    keyboard.append([InlineKeyboardButton("Меню", callback_data=MENU)])
    if cart["data"]:
        keyboard.append(
            [InlineKeyboardButton("Оформить заказ", callback_data=CHECKOUT)]
        )
    update.effective_message.reply_text(
        order,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    update.effective_message.delete()
    return CART


def remove_from_cart(update, context):
    query = update.callback_query
    query.answer()
    prod_id, quantity = query.data.split()
    quantity = int(quantity) - 1
    store.update_cart_item(update.effective_user.id, prod_id, quantity)
    return show_cart(update, context)


def handle_checkout(update, context):
    send_location = KeyboardButton("Отправить координаты", request_location=True)
    update.effective_message.reply_text(
        "Пожалуйста отправьте ваши координаты или напишите адрес доставки:",
        reply_markup=ReplyKeyboardMarkup(
            [[send_location]], resize_keyboard=True, one_time_keyboard=True
        ),
    )
    update.effective_message.delete()
    return CHECKOUT


def handle_location(update, context):
    if (location := utils.get_customer_location(update.message)) is None:
        update.effective_message.reply_text(
            "Не удалось определить ваше местоположение, попробуйте ещё раз."
        )
        return CHECKOUT

    utils.save_customer_location(location)
    context.chat_data["delivery"] = utils.get_delivery_info(location)
    keyboard = [
        [
            InlineKeyboardButton("Доставить", callback_data="deliver"),
            InlineKeyboardButton("Самовывоз", callback_data="pickup"),
        ]
    ]
    if context.chat_data["delivery"].distance > DELIVERY_RANGE:
        keyboard[0].pop(0)

    update.effective_message.reply_text(
        context.chat_data["delivery"].message,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return PAYMENT


def show_invoice(update, context):
    query = update.callback_query
    query.answer()
    context.chat_data["shipping"] = query.data

    order_id = f"{update.effective_user.id}-{int(time.time())}"
    cart = store.get_cart_items(update.effective_user.id)
    price = int(cart["meta"]["display_price"]["with_tax"]["formatted"])

    if context.chat_data["shipping"] == "deliver":
        delivery_cost = context.chat_data["delivery"].cost
    else:
        delivery_cost = 0

    prices = [
        LabeledPrice("Заказ", price * 100),
        LabeledPrice("Доставка", delivery_cost * 100),
    ]
    context.bot.send_invoice(
        chat_id=update.effective_user.id,
        title=f"Оплата заказа № {order_id}",
        description=ui.make_order_description(cart),
        payload="dadapizza",
        provider_token=os.environ["PAYMENT_PROVIDER"],
        currency="RUB",
        prices=prices,
    )
    update.effective_message.delete()
    return PAYMENT


def handle_payment(update, context):
    query = update.pre_checkout_query
    if query.invoice_payload != "dadapizza":
        query.answer(ok=False, error_message="Ошибка оплаты")
    else:
        query.answer(ok=True)
    return PAYMENT


def finalize_order(update, context):
    if context.chat_data["shipping"] == "deliver":
        update.effective_message.reply_text(
            "Спасибо за заказ!\nДоставим вашу пиццу в течение часа."
        )
        handle_delivery(update, context)
    else:
        update.effective_message.reply_text(
            f"Ваш заказ будет готов через 45 минут.\nЖдём вас по адресу: {context.chat_data['delivery'].shop}"
        )
    store.delete_cart(update.effective_user.id)
    return ConversationHandler.END


def handle_delivery(update, context):
    delivery = context.chat_data["delivery"]
    cart = store.get_cart_items(update.effective_user.id)
    order = ui.make_order(cart, delivery)

    context.bot.send_message(chat_id=delivery.deliveryman, text=order)
    context.bot.send_location(
        chat_id=delivery.deliveryman,
        latitude=delivery.latitude,
        longitude=delivery.longitude,
    )
    context.job_queue.run_once(checkup, CHECK_AFTER, context=update.effective_user.id)


def checkup(context):
    msg = "Приятного аппетита!\n*место для рекламы*\n*что делать если пицца не пришла*"
    context.bot.send_message(chat_id=context.job.context, text=msg)


def cancel(update, context):
    update.effective_message.reply_text("Всего хорошего! Будем рады видеть вас снова.")


def error(update, context):
    logger.error(f'Update "{update}" caused error "{context.error}"')


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    load_dotenv()

    updater = Updater(os.environ["TELEGRAM_TOKEN"])
    dispatcher = updater.dispatcher

    shop_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                CallbackQueryHandler(show_menu, pattern="^(-1|1)$"),
                CallbackQueryHandler(show_cart, pattern=CART),
                CallbackQueryHandler(show_product),
            ],
            PRODUCT: [
                CallbackQueryHandler(show_menu, pattern=MENU),
                CallbackQueryHandler(show_cart, pattern=CART),
                CallbackQueryHandler(add_to_cart),
            ],
            CART: [
                CallbackQueryHandler(show_menu, pattern=MENU),
                CallbackQueryHandler(handle_checkout, pattern=CHECKOUT),
                CallbackQueryHandler(remove_from_cart),
            ],
            CHECKOUT: [
                MessageHandler(
                    (Filters.location | Filters.text) & ~Filters.command,
                    handle_location,
                ),
                CallbackQueryHandler(show_invoice, pattern=PAYMENT),
            ],
            PAYMENT: [
                CallbackQueryHandler(show_invoice),
                PreCheckoutQueryHandler(handle_payment),
                MessageHandler(Filters.successful_payment, finalize_order),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_chat=False,
    )
    dispatcher.add_handler(shop_handler)
    dispatcher.add_error_handler(error)
    dispatcher.bot_data["menu"] = ui.make_menu()

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

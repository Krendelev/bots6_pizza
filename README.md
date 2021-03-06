# Бот-магазин

Бот для заказа пиццы. Пиццерия реализована на CMS [Elastic Path](https://www.elasticpath.com).

## Запуск

Скачайте код и установите зависимости.

```bash
$ python3 -m pip install -r requirements.txt
```

Создайте "пиццерию" в Elastic Path.
```bash
$ python3 setup.py
```

Запустите программу.
```bash
$ python3 main.py
```

## Настройки и переменные окружения

Сохраните переменные окружения в файл `.env`.

- `AUTH_URL`– эндпойнт авторизации CMS
- `BASE_URL`– базовый url для обращения к CMS
- `CLIENT_ID` – id администратора магазина
- `CLIENT_SECRET` – ключ доступа администратора
- `TELEGRAM_TOKEN` – API-ключ телеграм-бота
- `PAYMENT_PROVIDER` – API-ключ платёжной системы
- `GEOCODER_API_KEY` – API-ключ геокодера используемого для определения координат места (например [Яндекс](https://developer.tech.yandex.ru/services/)).
- `TELEGRAM_ID` - Telegram `id` доставщика (для тестирования используйте свой)

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).

import requests


def get_ton_rub_price():
    try:
        # Получаем курс TON/USDT
        ton_usdt = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=TONUSDT").json().get("price")
        if not ton_usdt:
            raise ValueError("Не удалось получить цену TON/USDT")

        # Получаем курс USDT/RUB
        usdt_rub = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTRUB").json().get("price")
        if not usdt_rub:
            raise ValueError("Не удалось получить цену USDT/RUB")

        # Рассчитываем цену TON/RUB
        ton_rub = float(ton_usdt) * float(usdt_rub)
        return round(ton_rub, 2)

    except Exception as e:
        return f"Ошибка: {e}"


def calculate_star_price(ton_price, stars_to_ton_ratio, stars_count=100):
    """
    Функция для расчета цены звезд
    :param ton_price: цена за 1 тонну
    :param stars_to_ton_ratio: соотношение для перевода звезд в тонны (например, 100 звезд это 0.45 тон)
    :param stars_count: количество звезд (по умолчанию 100)
    :return: словарь с результатами расчетов
    """
    try:
        # Расчет цены одной звезды
        total_price_for_stars = ton_price * stars_to_ton_ratio  # Цена за все звезды
        star_price = total_price_for_stars / stars_count  # Цена за одну звезду

        # Расчет по курсу 1.65
        standard_price_per_star = 1.65
        total_standard_price = standard_price_per_star * stars_count
        price_difference = standard_price_per_star - star_price

        return {
            'star_price': round(star_price, 2),
            'total_price': round(total_price_for_stars, 2),
            'standard_price': round(total_standard_price, 2),
            'price_difference': round(price_difference, 2),
            'ton_price': round(ton_price, 2)
        }
    except Exception as e:
        return f"Ошибка расчета: {e}"
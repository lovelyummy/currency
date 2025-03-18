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

def calculate_star_price(ton_price, stars_to_ton_ratio):
    """
    Функция для расчета цены одной звезды
    :param ton_price: цена за 1 тонну
    :param stars_to_ton_ratio: соотношение для перевода звезд в тонны (например, 100 звезд это 0.45 тон)
    :return: цена одной звезды
    """
    total_price_for_stars = ton_price * stars_to_ton_ratio  # Цена за все 100 звезд
    star_price = total_price_for_stars / 100  # Цена за одну звезду
    return round(star_price, 2)


if __name__ == "__main__":
    # Получаем цену за 1 тонну через API
    ton_price = get_ton_rub_price()

    # Проверяем, если произошла ошибка при получении цены
    if isinstance(ton_price, str) and ton_price.startswith("Ошибка"):
        print(ton_price)
    else:
        # Запрашиваем количество тонн для 100 звезд (например, 0.45 тон)
        stars_to_ton_ratio = float(input("Введите количество тонн для 100 звезд (например, 0.45): "))

        # Рассчитываем цену одной звезды
        star_price = calculate_star_price(ton_price, stars_to_ton_ratio)
        print(f"Цена одной звезды: {star_price} рублей")

        print(f"Текущая цена TON/RUB: {ton_price}")

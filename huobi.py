import requests
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from keyboards import get_inline_huobi_keyboard, get_main_menu_keyboard

# Создаем роутер для Huobi
huobi_router = Router()

# User-Agent для запросов к Huobi
HUOBI_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"

# Создаем класс состояний
class HuobiState(StatesGroup):
    waiting_for_amount_sell = State()  # Состояние ожидания ввода суммы для SELL
    waiting_for_amount_buy = State()  # Состояние ожидания ввода суммы для BUY


def get_huobi_p2p_data(amount: float, trade_type: str = "sell"):
    """
    Получает данные о P2P-предложениях на Huobi.

    :param amount: Сумма для фильтрации предложений.
    :param trade_type: Тип сделки ("sell" или "buy").
    :return: Словарь с данными о предложениях.
    """
    url = "https://www.htx.com/-/x/otc/v1/data/trade-market"
    params = {
        "coinId": 2,  # USDT
        "currency": 172,  # CNY
        "tradeType": trade_type,  # "sell" или "buy"
        "currPage": 1,  # Page 1
        "payMethod": 0,  # All payment methods
        "acceptOrder": 0,
        "country": "",
        "blockType": "general",  # General offers
        "online": 1,  # Only online sellers
        "range": 0,
        "amount": amount,  # Минимальная сумма
        "isThumbsUp": "false",
        "isMerchant": "false",
        "isTraded": "false",
        "onlyTradable": "false",
        "isFollowed": "false",
        "makerCompleteRate": 0
    }

    headers = {
        "User-Agent": HUOBI_USER_AGENT
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if data["code"] == 200:
        return data
    else:
        raise Exception(f"Huobi API Error: {data['message']}")


def parse_huobi_p2p_data(data):
    """
    Парсит данные о P2P-предложениях Huobi.

    :param data: Данные, полученные от Huobi API.
    :return: Словарь с минимальной, максимальной и средней ценой, а также количеством предложений с Alipay и WeChat.
    """
    prices = []  # Для хранения всех цен
    alipay_count = 0  # Счетчик Alipay
    wechat_count = 0  # Счетчик WeChat

    # Ограничиваемся первыми 10 предложениями
    for offer in data["data"][:10]:
        price = float(offer["price"])
        prices.append(price)

        # Подсчет методов оплаты
        payment_methods = [m["name"] for m in offer["payMethods"]]
        if "Alipay" in payment_methods:
            alipay_count += 1
        if "WeChat" in payment_methods:
            wechat_count += 1

    if prices:
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)

        return {
            "min_price": min_price,
            "max_price": max_price,
            "avg_price": avg_price,
            "alipay_count": alipay_count,
            "wechat_count": wechat_count
        }
    else:
        return None


# Обработчик нажатия на кнопку "Huobi"
@huobi_router.callback_query(F.data == "huobi")
async def huobi_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "🇨🇳 Huobi Menu:\n\n"
        "💱 *P2P Market (USDT/CNY):*\n"
        "1️⃣ *Sell* – P2P price based on the last 10 sellers of USDT.\n"
        "2️⃣ *Buy* – P2P price based on the last 10 buyers of USDT.",
        reply_markup=get_inline_huobi_keyboard()  # Клавиатура для Huobi
    )


# Обработчик нажатия на кнопку "USDT/CNY SELL"
@huobi_router.callback_query(F.data == "usdtcnysell")
async def usdtcnysell_callback(callback: CallbackQuery, state: FSMContext):
    # Сохраняем message_id меню
    await state.update_data(menu_message_id=callback.message.message_id)

    # Устанавливаем состояние ожидания ввода суммы для SELL
    await state.set_state(HuobiState.waiting_for_amount_sell)

    # Редактируем сообщение с меню, добавляя запрос на ввод суммы
    await callback.message.edit_text(
        "🇨🇳 Huobi P2P (SELL):\n\n"
        "Введите сумму в CNY для SELL (ОТ 100):",
        reply_markup=get_inline_huobi_keyboard()  # Сохраняем клавиатуру
    )


# Обработчик нажатия на кнопку "USDT/CNY BUY"
@huobi_router.callback_query(F.data == "usdtcnybuy")
async def usdtcnybuy_callback(callback: CallbackQuery, state: FSMContext):
    # Сохраняем message_id меню
    await state.update_data(menu_message_id=callback.message.message_id)

    # Устанавливаем состояние ожидания ввода суммы для BUY
    await state.set_state(HuobiState.waiting_for_amount_buy)

    # Редактируем сообщение с меню, добавляя запрос на ввод суммы
    await callback.message.edit_text(
        "🇨🇳 Huobi P2P (BUY):\n\n"
        "Введите сумму в CNY для BUY (ОТ 100):",
        reply_markup=get_inline_huobi_keyboard()  # Сохраняем клавиатуру
    )


# Обработчик текстовых сообщений для Huobi (SELL)
@huobi_router.message(HuobiState.waiting_for_amount_sell)
async def handle_huobi_sell_amount(message: Message, state: FSMContext):
    # Получаем сохраненный message_id меню
    state_data = await state.get_data()
    menu_message_id = state_data.get("menu_message_id")

    try:
        # Пытаемся преобразовать введенный текст в число
        amount = float(message.text)

        # Проверяем, что сумма больше или равна 100
        if amount < 100:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=menu_message_id,
                text="🇨🇳 Huobi P2P (SELL):\n\n"
                     "❌ Пожалуйста, введите корректную сумму в CNY (ОТ 100).",
                reply_markup=get_inline_huobi_keyboard()  # Сохраняем клавиатуру
            )
            return

        # Получаем данные от Huobi API для SELL
        data = get_huobi_p2p_data(amount, trade_type="sell")

        # Парсим данные
        parsed_data = parse_huobi_p2p_data(data)

        if parsed_data:
            result_text = (
                f"🇨🇳 Huobi P2P Data (SELL):\n\n"
                f"📉 Min Price: {parsed_data['min_price']} CNY\n"
                f"📈 Max Price: {parsed_data['max_price']} CNY\n"
                f"📊 Avg Price: {parsed_data['avg_price']:.2f} CNY\n"
                f"🔵 Alipay Offers: {parsed_data['alipay_count']}/10\n"
                f"🟢 WeChat Offers: {parsed_data['wechat_count']}/10"
            )
        else:
            result_text = "🇨🇳 Huobi P2P (SELL):\n\n❌ No offers found for the specified amount."

        # Редактируем сообщение с меню, добавляя результат
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=menu_message_id,
            text=result_text,
            reply_markup=get_inline_huobi_keyboard()  # Сохраняем клавиатуру
        )

    except ValueError:
        # Если введено некорректное значение (не число)
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=menu_message_id,
            text="🇨🇳 Huobi P2P (SELL):\n\n"
                 "❌ Пожалуйста, введите корректную сумму в CNY (ОТ 100).",
            reply_markup=get_inline_huobi_keyboard()  # Сохраняем клавиатуру
        )
    except Exception as e:
        # Если произошла другая ошибка
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=menu_message_id,
            text=f"🇨🇳 Huobi P2P (SELL):\n\n⚠ Error: {str(e)}",
            reply_markup=get_inline_huobi_keyboard()  # Сохраняем клавиатуру
        )

    # Сбрасываем состояние
    await state.clear()


# Обработчик текстовых сообщений для Huobi (BUY)
@huobi_router.message(HuobiState.waiting_for_amount_buy)
async def handle_huobi_buy_amount(message: Message, state: FSMContext):
    # Получаем сохраненный message_id меню
    state_data = await state.get_data()
    menu_message_id = state_data.get("menu_message_id")

    try:
        # Пытаемся преобразовать введенный текст в число
        amount = float(message.text)

        # Проверяем, что сумма больше или равна 100
        if amount < 100:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=menu_message_id,
                text="🇨🇳 Huobi P2P (BUY):\n\n"
                     "❌ Пожалуйста, введите корректную сумму в CNY (ОТ 100).",
                reply_markup=get_inline_huobi_keyboard()  # Сохраняем клавиатуру
            )
            return

        # Получаем данные от Huobi API для BUY
        data = get_huobi_p2p_data(amount, trade_type="buy")

        # Парсим данные
        parsed_data = parse_huobi_p2p_data(data)

        if parsed_data:
            result_text = (
                f"🇨🇳 Huobi P2P Data (BUY):\n\n"
                f"📉 Min Price: {parsed_data['min_price']} CNY\n"
                f"📈 Max Price: {parsed_data['max_price']} CNY\n"
                f"📊 Avg Price: {parsed_data['avg_price']:.2f} CNY\n"
                f"🔵 Alipay Offers: {parsed_data['alipay_count']}/10\n"
                f"🟢 WeChat Offers: {parsed_data['wechat_count']}/10"
            )
        else:
            result_text = "🇨🇳 Huobi P2P (BUY):\n\n❌ No offers found for the specified amount."

        # Редактируем сообщение с меню, добавляя результат
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=menu_message_id,
            text=result_text,
            reply_markup=get_inline_huobi_keyboard()  # Сохраняем клавиатуру
        )

    except ValueError:
        # Если введено некорректное значение (не число)
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=menu_message_id,
            text="🇨🇳 Huobi P2P (BUY):\n\n"
                 "❌ Пожалуйста, введите корректную сумму в CNY (ОТ 100).",
            reply_markup=get_inline_huobi_keyboard()  # Сохраняем клавиатуру
        )
    except Exception as e:
        # Если произошла другая ошибка
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=menu_message_id,
            text=f"🇨🇳 Huobi P2P (BUY):\n\n⚠ Error: {str(e)}",
            reply_markup=get_inline_huobi_keyboard()  # Сохраняем клавиатуру
        )

    # Сбрасываем состояние
    await state.clear()
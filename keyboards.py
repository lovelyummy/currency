from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    """
    Создает инлайн-клавиатуру для основного меню.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # Первая строка с кнопками Bybit и Huobi
            [
                InlineKeyboardButton(text="💲 Bybit", callback_data="bybit"),
                InlineKeyboardButton(text="🇨🇳 Huobi", callback_data="huobi")
            ],
            # Вторая строка с кнопкой Support
            [
                InlineKeyboardButton(text="🧑‍💻 Support", url="https://t.me/ryotto")
            ],
            # Третья строка с кнопкой Stars
            [
                InlineKeyboardButton(text="⭐️ Stars", callback_data="stars")
            ]
        ]
    )
    return keyboard

def get_inline_bybit_keyboard():
    """
    Создает инлайн-клавиатуру для меню Bybit.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # Первая строка с кнопками
            [
                InlineKeyboardButton(text="🟠 BTC/USDT", callback_data="btcusdt"),
                InlineKeyboardButton(text="🟣 ETH/USDT", callback_data="ethusdt")
            ],
            # Вторая строка с кнопками
            [
                InlineKeyboardButton(text="🇷🇺 USDT/RUB Buy🟢", callback_data="usdtbuyrub"),
                InlineKeyboardButton(text="🇷🇺 USDT/RUB Sell🔴", callback_data="usdtrubsell")
            ],
            # Третья строка с кнопкой "Back"
            [
                InlineKeyboardButton(text="🔙 Back", callback_data="back")
            ]
        ]
    )
    return keyboard

def get_inline_huobi_keyboard():
    """
    Создает инлайн-клавиатуру для меню Huobi.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # Первая строка с кнопками USDT/CNY SELL и USDT/CNY BUY
            [
                InlineKeyboardButton(text="🇨🇳 USDT/CNY Buy🟢", callback_data="usdtcnybuy"),
                InlineKeyboardButton(text="🇨🇳 USDT/CNY Sell🔴", callback_data="usdtcnysell")
            ],
            # Вторая строка с кнопкой "Back"
            [
                InlineKeyboardButton(text="🔙 Back", callback_data="back")
            ]
        ]
    )
    return keyboard
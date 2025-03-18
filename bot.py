import logging
import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, BotCommand, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
from stars import get_ton_rub_price, calculate_star_price

# Импортируем клавиатуру из keyboards.py
from keyboards import get_main_menu_keyboard, get_inline_bybit_keyboard

# Импортируем роутер Huobi из huobi.py
from huobi import huobi_router

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Создаем бота и диспетчер
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Создаем роутер
router = Router()

# Создаем сессию для подключения к основной сети Bybit
session = HTTP(testnet=False)

# Определяем состояния FSM
class Form(StatesGroup):
    amount = State()  # Уже есть
    stars_ratio = State()  #

# Функция для установки команд меню
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
    ]
    await bot.set_my_commands(commands)

# Обработчик команды /start
@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        "👋 Hello! I am a currency bot that can show you the current price of BTC, ETH and P2P rates. Currently only for Bybit and Huobi.\n\n"
        "Choose one of the options below:",
        reply_markup=get_main_menu_keyboard()  # Используем инлайн-клавиатуру
    )

@router.callback_query(F.data == "stars")
async def stars_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите количество тонн для 100 звезд (например, 0.45):",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Назад", callback_data="back")]
        ])
    )
    await state.set_state(Form.stars_ratio)

@router.message(Form.stars_ratio)  # Используем Form.stars_ratio
async def process_stars_ratio(message: Message, state: FSMContext):
    try:
        stars_to_ton_ratio = float(message.text)
        ton_price = get_ton_rub_price()

        if isinstance(ton_price, str) and ton_price.startswith("Ошибка"):
            await message.answer(ton_price, reply_markup=get_main_menu_keyboard())
            await state.clear()
            return

        star_price = calculate_star_price(ton_price, stars_to_ton_ratio)
        result_text = (
            f"⭐️ *Цена одной звезды:* {star_price} рублей\n"
            f"💎 *Текущая цена TON/RUB:* {ton_price} рублей"
        )

        await message.answer(result_text, reply_markup=get_main_menu_keyboard(), parse_mode=ParseMode.MARKDOWN)
        await state.clear()

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число (например, 0.45).")
    except Exception as e:
        logger.error(f"Error in process_stars_ratio: {e}")
        await message.answer(f"⚠ Ошибка: {str(e)}")
        await state.clear()

# Обработчик нажатия на кнопку "Bybit"
@router.callback_query(F.data == "bybit")
async def bybit_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "💲 Bybit Menu:\n\n"
        "💰 *SPOT Market:*\n"
        "1️⃣ *BTC/USDT* – Current price of BTC on Bybit SPOT.\n"
        "2️⃣ *ETH/USDT* – Current price of ETH on Bybit SPOT.\n\n"
        "💱 *P2P Market (USDT/RUB):*\n"
        "3️⃣ *Buy* – P2P price for buying USDT.\n"
        "4️⃣ *Sell* – P2P price for selling USDT.",
        reply_markup=get_inline_bybit_keyboard()  # Клавиатура для Bybit
    )

# Обработчик нажатия на кнопку "Back"
@router.callback_query(F.data == "back")
async def back_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "👋 Hello! I am a currency bot that can show you the current price of BTC, ETH and P2P rates. Currently only for Bybit and Huobi.\n\n"
        "Choose one of the options below:",
        reply_markup=get_main_menu_keyboard()  # Возвращаемся к главному меню
    )

@router.callback_query(F.data == "btcusdt")
async def btcusdt_callback(callback: CallbackQuery):
    try:
        # Запрашиваем тикеры для пары BTC/USDT
        response = session.get_tickers(category="spot", symbol="BTCUSDT")
        data = response['result']['list'][0]

        # Извлекаем нужные данные
        symbol = data['symbol']
        last_price = data['lastPrice']
        high_price = data['highPrice24h']
        low_price = data['lowPrice24h']

        # Формируем ответ
        result = (
            f"🟠 *{symbol}*\n"
            f"💰 *Current price:* {last_price} USDT\n"
            f"📈 *24h High:* {high_price} USDT\n"
            f"📉 *24h Low:* {low_price} USDT"
        )

        # Редактируем сообщение, оставляя только результат и клавиатуру
        await callback.message.edit_text(
            result,
            reply_markup=get_inline_bybit_keyboard(),  # Сохраняем клавиатуру
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        logger.error(f"Error in btcusdt_callback: {e}")
        await callback.message.edit_text(f"⚠ Error: {str(e)}")


@router.callback_query(F.data == "ethusdt")
async def ethusdt_callback(callback: CallbackQuery):
    try:
        # Запрашиваем тикеры для пары ETH/USDT
        response = session.get_tickers(category="spot", symbol="ETHUSDT")
        data = response['result']['list'][0]

        # Извлекаем нужные данные
        symbol = data['symbol']
        last_price = data['lastPrice']
        high_price = data['highPrice24h']
        low_price = data['lowPrice24h']

        # Формируем ответ
        result = (
            f"🟠 *{symbol}*\n"
            f"💰 *Current price:* {last_price} USDT\n"
            f"📈 *24h High:* {high_price} USDT\n"
            f"📉 *24h Low:* {low_price} USDT"
        )

        # Редактируем сообщение, оставляя только результат и клавиатуру
        await callback.message.edit_text(
            result,
            reply_markup=get_inline_bybit_keyboard(),  # Сохраняем клавиатуру
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        logger.error(f"Error in ethusdt_callback: {e}")
        await callback.message.edit_text(f"⚠ Error: {str(e)}")

# Добавьте этот код в ваш основной файл бота

@router.inline_query()
async def inline_mode_handler(inline_query: InlineQuery):
    query = inline_query.query.lower()  # Получаем текст запроса

    # Обработка запроса для BTC
    if query == "btc":
        try:
            # Запрашиваем цену BTC (используем тот же код, что и для кнопки)
            response = session.get_tickers(category="spot", symbol="BTCUSDT")
            data = response['result']['list'][0]
            symbol = data['symbol']
            last_price = data['lastPrice']
            high_price = data['highPrice24h']
            low_price = data['lowPrice24h']

            # Формируем ответ (тот же текст, что и для кнопки)
            result_text = (
                f"🟠 *{symbol}*\n"
                f"💰 *Current price:* {last_price} USDT\n"
                f"📈 *24h High:* {high_price} USDT\n"
                f"📉 *24h Low:* {low_price} USDT"
            )

            # Создаем результат для inline-режима
            result = InlineQueryResultArticle(
                id="1",
                title="💰 Текущая цена BTC",
                input_message_content=InputTextMessageContent(
                    message_text=result_text,
                    parse_mode=ParseMode.MARKDOWN
                ),
                description=f"Цена BTC: {last_price} USDT",
            )

            # Отправляем результат
            await inline_query.answer([result], cache_time=1)

        except Exception as e:
            logger.error(f"Error in inline BTC query: {e}")
            await inline_query.answer(
                [InlineQueryResultArticle(
                    id="error",
                    title="⚠ Ошибка",
                    input_message_content=InputTextMessageContent(
                        message_text="Произошла ошибка при получении цены BTC."
                    )
                )],
                cache_time=1
            )

    # Обработка запроса для ETH
    elif query == "eth":
        try:
            # Запрашиваем цену ETH (используем тот же код, что и для кнопки)
            response = session.get_tickers(category="spot", symbol="ETHUSDT")
            data = response['result']['list'][0]
            symbol = data['symbol']
            last_price = data['lastPrice']
            high_price = data['highPrice24h']
            low_price = data['lowPrice24h']

            # Формируем ответ (тот же текст, что и для кнопки)
            result_text = (
                f"🟣 *{symbol}*\n"
                f"💰 *Current price:* {last_price} USDT\n"
                f"📈 *24h High:* {high_price} USDT\n"
                f"📉 *24h Low:* {low_price} USDT"
            )

            # Создаем результат для inline-режима
            result = InlineQueryResultArticle(
                id="2",
                title="💰 Текущая цена ETH",
                input_message_content=InputTextMessageContent(
                    message_text=result_text,
                    parse_mode=ParseMode.MARKDOWN
                ),
                description=f"Цена ETH: {last_price} USDT",
            )

            # Отправляем результат
            await inline_query.answer([result], cache_time=1)

        except Exception as e:
            logger.error(f"Error in inline ETH query: {e}")
            await inline_query.answer(
                [InlineQueryResultArticle(
                    id="error",
                    title="⚠ Ошибка",
                    input_message_content=InputTextMessageContent(
                        message_text="Произошла ошибка при получении цены ETH."
                    )
                )],
                cache_time=1
            )

    # Если запрос не распознан
    else:
        await inline_query.answer(
            [InlineQueryResultArticle(
                id="unknown",
                title="❌ Неизвестная команда",
                input_message_content=InputTextMessageContent(
                    message_text="Используйте `btc` или `eth` для получения цен."
                )
            )],
            cache_time=1
        )

@router.callback_query(F.data == "usdtbuyrub")
async def usdtbuyrub_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите сумму рублей для покупки USDT (минимум 1000) might be delay 2-5sec:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Назад", callback_data="bybit")]
        ])
    )
    await state.set_state(Form.amount)
    await state.update_data(action="buy")

@router.callback_query(F.data == "usdtrubsell")
async def usdtrubsell_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите сумму рублей для продажи USDT (минимум 1000) might be delay 2-5sec:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Назад", callback_data="bybit")]
        ])
    )
    await state.set_state(Form.amount)
    await state.update_data(action="sell")

@router.message(Form.amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount < 1000:
            await message.answer("Минимальная сумма 1000. Пожалуйста, введите сумму снова. might be delay 2-5sec")
            return

        data = await state.get_data()
        action = data.get("action")

        url = "https://api2.bybit.com/fiat/otc/item/online"
        side = "1" if action == "buy" else "0"

        payload = {
            "userId": "",
            "tokenId": "USDT",
            "currencyId": "RUB",
            "payment": ["382", "581", "75"],
            "side": side,
            "size": "8",
            "page": "1",
            "amount": str(amount),
            "vaMaker": False,
            "bulkMaker": False,
            "canTrade": True,
            "verificationFilter": 0,
            "sortType": "TRADE_PRICE",
            "paymentPeriod": [],
            "itemRegion": 1
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                result = await response.json()

        prices = []
        if 'result' in result and 'items' in result['result']:
            items = result['result']['items']
            for item in items:
                price = float(item['price'])
                prices.append(price)

            max_price = max(prices)
            min_price = min(prices)
            avg_price = sum(prices) / len(prices)

            result_text = (
                f"✅ {action.upper()} Rate - USDT/RUB:\n"
                f"📈 Max price: {max_price} ₽\n"
                f"📉 Min price: {min_price} ₽\n"
                f"📊 Average price: {avg_price:.2f} ₽"
            )
        else:
            result_text = "Data not found or response structure is different."

        await message.answer(
            result_text,
            reply_markup=get_inline_bybit_keyboard()
        )
        await state.clear()

    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму.")
    except Exception as e:
        logger.error(f"Error in process_amount: {e}")
        await message.answer(f"⚠ Error: {str(e)}")
        await state.clear()

# Обработчик для всех текстовых сообщений (возвращает в главное меню)
@router.message(F.text)
async def handle_any_message(message: Message):
    # Если сообщение не команда, возвращаем пользователя в главное меню
    if not message.text.startswith("/"):
        await message.answer(
            "👋 Hello! I am a currency bot that can show you the current price of BTC, ETH and P2P rates. Currently only for Bybit and Huobi.\n\n"
            "Choose one of the options below:",
            reply_markup=get_main_menu_keyboard()  # Возвращаемся к главному меню
        )





# Функция запуска бота
async def main():
    # Устанавливаем команды меню
    await set_bot_commands(bot)

    # Подключаем роутер Huobi
    dp.include_router(huobi_router)

    # Подключаем основной роутер
    dp.include_router(router)

    # Удаляем вебхук (если был)
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
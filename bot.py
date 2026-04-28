
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("8566316598:AAGIogEV1Yduonc06ElZjzYwyoW86jpBr5g")
TWELVE_DATA_API_KEY = os.getenv("2eced3d788e24f03818e17d5b79c7db4")


def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False,
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    text = "Crypto Prices:\n\n"
    for coin in data:
        name = coin["name"]
        symbol = coin["symbol"].upper()
        price = coin["current_price"]
        change = coin.get("price_change_percentage_24h", 0)
        text += f"{name} ({symbol}) - ${price:,} | 24h: {change:.2f}%\n"

    return text


def get_forex_prices():
    pairs = ["EUR/USD", "GBP/USD", "USD/NGN", "USD/JPY", "USD/CAD"]
    text = "Forex Prices:\n\n"

    for pair in pairs:
        url = "https://api.twelvedata.com/exchange_rate"
        params = {
            "symbol": pair,
            "apikey": TWELVE_DATA_API_KEY,
        }

        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        rate = data.get("rate")
        if rate:
            text += f"{pair} - {float(rate):,.4f}\n"
        else:
            text += f"{pair} - Not available\n"

    return text


def get_stock_prices():
    symbols = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"]
    text = "Stock Prices:\n\n"

    for symbol in symbols:
        url = "https://api.twelvedata.com/quote"
        params = {
            "symbol": symbol,
            "apikey": TWELVE_DATA_API_KEY,
        }

        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        price = data.get("close") or data.get("price")
        change = data.get("percent_change")

        if price:
            if change is not None:
                text += f"{symbol} - ${float(price):,.2f} | {change}%\n"
            else:
                text += f"{symbol} - ${float(price):,.2f}\n"
        else:
            text += f"{symbol} - Not available\n"

    return text


def split_message(text, size=4000):
    return [text[i:i + size] for i in range(0, len(text), size)]


async def send_text(update: Update, text: str):
    for part in split_message(text):
        await update.message.reply_text(part)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to your Market Price Bot.\n\n"
        "Use these commands:\n"
        "/crypto - Crypto prices\n"
        "/forex - Forex prices\n"
        "/stocks - Stock prices"
    )


async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await send_text(update, get_crypto_prices())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def forex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await send_text(update, get_forex_prices())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await send_text(update, get_stock_prices())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing")

    if not TWELVE_DATA_API_KEY:
        raise ValueError("TWELVE_DATA_API_KEY is missing")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("crypto", crypto))
    app.add_handler(CommandHandler("forex", forex))
    app.add_handler(CommandHandler("stocks", stocks))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

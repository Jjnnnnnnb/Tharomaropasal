import telebot
import openai
import requests
from bs4 import BeautifulSoup
from telebot import types

# ✅ Hardcoded credentials (for testing purpose)
BOT_TOKEN = "7614169168:AAHWTWxozB9zeu4OK7Yay6Ythee4lPNENio"
OPENAI_API_KEY = "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"
AMAZON_AFFILIATE_TAG = "nepdostroe-20"

# 🔧 Setup OpenAI and Telegram bot
openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(BOT_TOKEN)

# ▶️ /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Welcome to SastoKhojBot!\nSend me a product name or food item to search.")

# 💬 Handle any message
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    query = message.text.strip()
    if not query:
        bot.reply_to(message, "❗Please enter something to search.")
        return

    bot.send_chat_action(message.chat.id, 'typing')

    # 🛒 Amazon search URL
    amazon_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}&tag={AMAZON_AFFILIATE_TAG}"

    # 🤖 AI Suggestion
    try:
        ai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Suggest affordable options for: {query}"}],
            max_tokens=150
        )
        suggestion = ai_response.choices[0].message.content.strip()
    except Exception as e:
        suggestion = "❌ Failed to get suggestion from AI."

    # 📦 Send result
    bot.send_message(
        message.chat.id,
        f"🔎 **Search Query**: `{query}`\n\n🛒 **Amazon Link**:\n{amazon_url}\n\n🤖 **AI Suggestion**:\n{suggestion}",
        parse_mode="Markdown"
    )

# ♾️ Keep bot running
bot.infinity_polling()
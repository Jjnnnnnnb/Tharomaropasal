# === IMPORTS ===
import telebot, openai, requests, sqlite3, datetime, random
from bs4 import BeautifulSoup
from telebot import types

# === SETUP ===
bot = telebot.TeleBot('7614169168:AAHWTWxozB9zeu4OK7Yay6Ythee4lPNENio')
openai.api_key = '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'
AFFILIATE_ID = 'nepdostroe-20'

# === DATABASE ===
db = sqlite3.connect("users.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, coins INTEGER, energy INTEGER, ref TEXT, last_claim TEXT)")
db.commit()

def user_setup(user_id):
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (id, coins, energy, ref, last_claim) VALUES (?, ?, ?, ?, ?)", (user_id, 0, 20, '', ''))
        db.commit()

# === START COMMAND ===
@bot.message_handler(commands=['start'])
def start(m):
    user_setup(m.chat.id)
    ref = m.text.split()[1] if len(m.text.split()) > 1 else ''
    if ref and ref != str(m.chat.id):
        cursor.execute("UPDATE users SET ref=? WHERE id=? AND ref=''", (ref, m.chat.id))
        cursor.execute("UPDATE users SET coins = coins + 10 WHERE id=?", (int(ref),))
        db.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("ðŸ’° Tap to Earn", "ðŸŽ Daily Reward", "ðŸ‘¥ Invite", "ðŸ›’ Shop Search")
    markup.add("ðŸ¤– AI Chat", "ðŸŽ¨ AI Image", "ðŸŽ® Spin", "ðŸ“¤ Withdraw")
    bot.send_message(m.chat.id, "ðŸŽ‰ Welcome to NEPDO Bot! Earn $ND coins, shop smart, and chat with AI!", reply_markup=markup)

# === TAP TO EARN ===
@bot.message_handler(func=lambda m: m.text=="ðŸ’° Tap to Earn")
def tap(m):
    user_setup(m.chat.id)
    cursor.execute("SELECT energy FROM users WHERE id=?", (m.chat.id,))
    energy = cursor.fetchone()[0]
    if energy > 0:
        earn = random.randint(1,3)
        cursor.execute("UPDATE users SET coins = coins + ?, energy = energy - 1 WHERE id=?", (earn, m.chat.id))
        db.commit()
        bot.send_message(m.chat.id, f"ðŸ–±ï¸ You tapped and earned {earn} $ND!")
    else:
        bot.send_message(m.chat.id, "âš¡ No energy! Wait for recharge or come back later.")

# === DAILY REWARD ===
@bot.message_handler(func=lambda m: m.text=="ðŸŽ Daily Reward")
def reward(m):
    now = str(datetime.date.today())
    cursor.execute("SELECT last_claim FROM users WHERE id=?", (m.chat.id,))
    last = cursor.fetchone()[0]
    if last != now:
        cursor.execute("UPDATE users SET coins = coins + 10, last_claim = ? WHERE id=?", (now, m.chat.id))
        db.commit()
        bot.send_message(m.chat.id, "âœ… You claimed your daily 10 $ND reward!")
    else:
        bot.send_message(m.chat.id, "ðŸ•’ You already claimed today's reward.")

# === REFERRAL ===
@bot.message_handler(func=lambda m: m.text=="ðŸ‘¥ Invite")
def refer(m):
    bot.send_message(m.chat.id, f"ðŸ”— Your referral link:
t.me/NEPDO_BOT?start={m.chat.id}")

# === SPIN GAME ===
@bot.message_handler(func=lambda m: m.text=="ðŸŽ® Spin")
def spin(m):
    n = random.choice([0, 2, 5, 10])
    cursor.execute("UPDATE users SET coins = coins + ? WHERE id=?", (n, m.chat.id))
    db.commit()
    bot.send_message(m.chat.id, f"ðŸŽ¯ You spun and won {n} $ND!")

# === SHOPPING SEARCH ===
@bot.message_handler(func=lambda m: m.text=="ðŸ›’ Shop Search")
def ask(m):
    bot.send_message(m.chat.id, "ðŸ” Send product name to search:")

@bot.message_handler(func=lambda m: m.reply_to_message and "product name" in m.reply_to_message.text)
def shop(m):
    q = m.text.strip()
    url = f"https://www.amazon.in/s?k={q.replace(' ','+')}&&tag={AFFILIATE_ID}"
    soup = BeautifulSoup(requests.get(url, headers={'User-Agent':'Mozilla'}).content, 'html.parser')
    item = soup.find('div', {'data-component-type': 's-search-result'})
    if item:
        title = item.h2.text
        image = item.img['src']
        link = "https://amazon.in" + item.h2.a['href'].split("?")[0] + f"?tag={AFFILIATE_ID}"
        price = item.find('span', {'class': 'a-price-whole'})
        bot.send_photo(m.chat.id, image, f"ðŸ›ï¸ {title}
ðŸ’° Price: â‚¹{price.text if price else 'N/A'}
ðŸ”— {link}")
    else:
        bot.send_message(m.chat.id, "âŒ Product not found.")

# === AI CHAT ===
@bot.message_handler(func=lambda m: m.text=="ðŸ¤– AI Chat")
def aichat(m):
    msg = bot.send_message(m.chat.id, "ðŸ’¬ Send your question for AI:")
    bot.register_next_step_handler(msg, chat_response)

def chat_response(m):
    res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role":"user", "content": m.text}])
    bot.send_message(m.chat.id, res['choices'][0]['message']['content'])

# === AI IMAGE ===
@bot.message_handler(func=lambda m: m.text=="ðŸŽ¨ AI Image")
def aiimg(m):
    msg = bot.send_message(m.chat.id, "ðŸ–¼ï¸ Send prompt for image:")
    bot.register_next_step_handler(msg, imggen)

def i

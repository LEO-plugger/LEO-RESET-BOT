import telebot
from telebot import types
import requests, uuid, string, random
import pyfiglet

# 🔐 Your saved token
BOT_TOKEN = '7879738528:AAEZaXJSVWRiF2r8q1n7djw4ZI22n0rlLxo'
bot = telebot.TeleBot(BOT_TOKEN)

# 🔄 State tracking
user_states = {}

# 🔧 IG reset logic
def send_ig_reset(user_input):
    if user_input.startswith("@"):
        return "🚫 Please send the username *without* '@'."

    headers = {
        "user-agent": (
            "Instagram 150.0.0.0.000 Android (29/10; 300dpi; 720x1440; "
            f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=16))}/"
            f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=16))}; "
            f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=16))}; "
            f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=16))}; "
            f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=16))}; en_GB;)"
        )
    }

    data = {
        "_csrftoken": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        "guid": str(uuid.uuid4()),
        "device_id": str(uuid.uuid4())
    }

    if "@" in user_input:
        data["user_email"] = user_input
    else:
        data["username"] = user_input

    response = requests.post(
        "https://i.instagram.com/api/v1/accounts/send_password_reset/",
        headers=headers,
        data=data
    )

    if "obfuscated_email" in response.text:
        return f"✅ *Success!*\nReset link sent to: `{user_input}`\n\n📨 Check your email or IG inbox."
    else:
        return f"❌ *Failed to send reset link.*\n\n`{response.text}`"

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    figlet = pyfiglet.figlet_format("LeoIGReset", font="slant")
    bot.send_message(message.chat.id, f"```{figlet}```", parse_mode="Markdown")

    welcome_msg = (
        f"✨ Welcome *{message.from_user.first_name}*!\n\n"
        "This bot sends real-time Instagram reset links ⚡\n"
        "💼 *Premium IG Tool by* [@leoplugger](https://t.me/leoplugger)\n\n"
        "🔽 Tap below to get started!"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Reset Instagram", callback_data="reset_ig"))
    markup.add(types.InlineKeyboardButton("💌 Contact Developer", url="https://t.me/leoplugger"))

    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=markup, disable_web_page_preview=True)

# /reset command
@bot.message_handler(commands=['reset'])
def manual_reset(message):
    prompt_reset(message)

# ask for username/email
def prompt_reset(message):
    msg = bot.send_message(message.chat.id,
                           "📩 *Reply to this message* with your Instagram email or username.",
                           parse_mode="Markdown")
    user_states[message.chat.id] = "awaiting_reset"

# button click
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.data == "reset_ig":
        prompt_reset(call.message)

# handle reply
@bot.message_handler(func=lambda msg: True)
def handle_input(msg):
    if user_states.get(msg.chat.id) == "awaiting_reset":
        user_input = msg.text.strip()
        bot.send_chat_action(msg.chat.id, "typing")
        result = send_ig_reset(user_input)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔁 Try Again", callback_data="reset_ig"))
        markup.add(types.InlineKeyboardButton("❤️ Made by @leoplugger", url="https://t.me/leoplugger"))

        bot.send_message(msg.chat.id, result, parse_mode="Markdown", reply_markup=markup)
        user_states[msg.chat.id] = None

# start the bot
bot.infinity_polling()

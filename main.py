import telebot
from datetime import datetime
import pytz
import threading
import time
import os
import logging

# === SET UP LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === BOT TOKEN ===
BOT_TOKEN = "8852534776:AAFQ08HdM-dzGQhcdUUpsmfEnZ1w9FBRn2Y"  # 🔴 Put your real bot token here
bot = telebot.TeleBot(BOT_TOKEN)

# === SHARED VARIABLES ===
print_lock = threading.Lock()
contact_logs = []

# === START COMMAND ===
@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        button = telebot.types.KeyboardButton(
            text="📲 Click Here",
            request_contact=True
        )

        markup.add(button)

        bot.send_message(
            message.chat.id,
            "👋 *Welcome to PLUS PRO!*\n\n"
            "📲 Please share your contact to continue.\n\n"
            "⚡ Powered by *PLUS PRO*",
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Error in welcome handler: {e}")

# === CONTACT HANDLER ===
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    try:
        contact = message.contact
        india_time = datetime.now(pytz.timezone("Asia/Kolkata"))
        weekday = india_time.strftime("%A")
        time_str = india_time.strftime("%I:%M %p")

        from_user = message.from_user
        tg_username = f"@{from_user.username}" if from_user.username else "❌ Not Available"
        chat_id = from_user.id
        first_name = from_user.first_name or "❓ Unknown"
        phone_number = contact.phone_number or "❓ Unknown"

        log = (
            f"\n📥 New Contact Received:\n"
            f"👤 Name     : {first_name}\n"
            f"📱 Phone    : {phone_number}\n"
            f"🔗 Username : {tg_username}\n"
            f"🆔 Chat ID  : {chat_id}\n"
            f"📅 Day      : {weekday}\n"
            f"🕒 Time     : {time_str}\n"
            f"📢 Powered by MT CODE\n"
            + "-" * 50
        )

        with print_lock:
            contact_logs.append(log)
            logger.info(f"New contact received from {first_name} ({phone_number})")

        bot.send_message(
            message.chat.id,
            "✅ *Contact received successfully!*\n\n🚀 Welcome to *USER TO INFO*",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Error in contact handler: {e}")
        try:
            bot.send_message(message.chat.id, "❌ Error processing contact. Please try again.")
        except:
            pass

# === CLEAR TERMINAL FUNCTION ===
def clear():
    try:
        os.system("clear" if os.name == "posix" else "cls")
    except:
        print("\n" * 100)

# === ANIMATION + LOG DISPLAY FUNCTION ===
def animate_running():
    frames = ["[■□□□□]", "[■■□□□]", "[■■■□□]", "[■■■■□]", "[■■■■■]", "[□■■■■]", "[□□■■■]", "[□□□■■]", "[□□□□■]"]
    while True:
        try:
            for frame in frames:
                with print_lock:
                    clear()
                    print("\033[1;31m" + "=" * 60 + "\033[0m")
                    print("\033[1;31m{:^60}\033[0m".format("✨ Powered by MT CODE"))
                    print("\n\033[1;32m{:^60}\033[0m\n".format(f"🤖 Bot Running {frame}"))
                    print("\033[1;31m" + "=" * 60 + "\033[0m")

                    print("\n\033[1;36m📬 Recent Contacts:\033[0m")
                    if contact_logs:
                        for log in contact_logs[-3:]:
                            print(log)
                    else:
                        print("No contacts received yet...")

                time.sleep(0.4)
        except Exception as e:
            logger.error(f"Error in animation: {e}")
            time.sleep(1)

# === BOT POLLING WITH ERROR HANDLING ===
def start_bot():
    while True:
        try:
            logger.info("🤖 Starting bot polling...")
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
            logger.info("🔄 Restarting bot in 10 seconds...")
            time.sleep(10)

# === MAIN EXECUTION ===
if __name__ == "__main__":
    try:
        animation_thread = threading.Thread(target=animate_running)
        animation_thread.daemon = True
        animation_thread.start()

        logger.info("🔧 Bot started successfully!")
        logger.info("📱 Bot is now running and waiting for contacts...")

        start_bot()

    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

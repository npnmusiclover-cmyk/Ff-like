import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import re

# =========================================================
#                    BOT TOKEN
# =========================================================

BOT_TOKEN = "8496595814:AAGribEBb_Uoba0f6p8tw2Lz8WES5uOziB0"

bot = telebot.TeleBot(BOT_TOKEN)

# =========================================================
#                 CHANNEL USERNAMES
# =========================================================

CHANNEL_1 = "@inffo_01"
CHANNEL_2 = "@plus_official01"

# =========================================================
#                    FREE FIRE API
# =========================================================

LIKE_API = "https://najmi-ob53-like-api.vercel.app/like"
API_KEY = "NJM"

# =========================================================
#                 FORCE JOIN CHECK
# =========================================================

def joined(user_id):

    try:

        ch1 = bot.get_chat_member(
            CHANNEL_1,
            user_id
        )

        ch2 = bot.get_chat_member(
            CHANNEL_2,
            user_id
        )

        allowed = [
            "member",
            "administrator",
            "creator"
        ]

        if ch1.status in allowed and ch2.status in allowed:
            return True

    except:
        return False

    return False

# =========================================================
#                      START CMD
# =========================================================

@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    if not joined(user_id):

        markup = InlineKeyboardMarkup()

        btn1 = InlineKeyboardButton(
            "📢 JOIN CHANNEL 1",
            url="https://t.me/inffo_01"
        )

        btn2 = InlineKeyboardButton(
            "📢 JOIN CHANNEL 2",
            url="https://t.me/plus_official01"
        )

        btn3 = InlineKeyboardButton(
            "✅ VERIFY",
            callback_data="verify"
        )

        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)

        bot.send_photo(
            message.chat.id,
            "https://i.imgur.com/6RL6hWH.jpeg",
            caption="""
🔥 WELCOME TO FREE FIRE LIKE BOT

━━━━━━━━━━━━━━━━━━━

✅ JOIN BOTH CHANNELS
✅ CLICK VERIFY BUTTON

━━━━━━━━━━━━━━━━━━━

⚡ AUTO LIKE SYSTEM
💎 FAST SERVER
🎮 FREE SERVICE
            """,
            reply_markup=markup
        )

        return

    bot.send_message(
        message.chat.id,
        """
🎮 FREE FIRE LIKE BOT ACTIVE

━━━━━━━━━━━━━━━━━━━

📌 SEND UID + REGION

EXAMPLE:
5513136279 ind

━━━━━━━━━━━━━━━━━━━

🌍 REGIONS:
ind
bd
sg
br
us

━━━━━━━━━━━━━━━━━━━
"""
    )

# =========================================================
#                   VERIFY BUTTON
# =========================================================

@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "verify":

        user_id = call.from_user.id

        if not joined(user_id):

            bot.answer_callback_query(
                call.id,
                "❌ JOIN BOTH CHANNELS FIRST",
                show_alert=True
            )

            return

        bot.edit_message_text(
            """
✅ VERIFICATION SUCCESSFUL

━━━━━━━━━━━━━━━━━━━

🎮 NOW SEND UID

EXAMPLE:
5513136279 ind

━━━━━━━━━━━━━━━━━━━
""",
            call.message.chat.id,
            call.message.message_id
        )

# =========================================================
#                    LIKE SYSTEM
# =========================================================

@bot.message_handler(func=lambda message: True)
def like_system(message):

    user_id = message.from_user.id

    if not joined(user_id):

        bot.send_message(
            message.chat.id,
            "❌ USE /start AND JOIN CHANNELS FIRST"
        )

        return

    text = message.text.strip()

    match = re.match(
        r"(\d+)\s+([a-zA-Z]+)",
        text
    )

    if not match:

        bot.send_message(
            message.chat.id,
            """
❌ WRONG FORMAT

━━━━━━━━━━━━━━━━━━━

✅ EXAMPLE:
5513136279 ind

━━━━━━━━━━━━━━━━━━━
"""
        )

        return

    uid = match.group(1)
    region = match.group(2).lower()

    wait = bot.send_message(
        message.chat.id,
        "⏳ SENDING LIKES..."
    )

    try:

        url = (
            f"{LIKE_API}"
            f"?uid={uid}"
            f"&server_name={region}"
            f"&key={API_KEY}"
        )

        response = requests.get(url).json()

        # =====================================================
        # RESPONSE HANDLE
        # =====================================================

        player_name = response.get(
            "player_name",
            "Unknown"
        )

        likes_before = response.get(
            "likes_before",
            0
        )

        likes_after = response.get(
            "likes_after",
            0
        )

        likes_added = response.get(
            "likes_given_by_api",
            50
        )

        failed = response.get(
            "failed",
            0
        )

        # =====================================================
        # FINAL MESSAGE
        # =====================================================

        final = f"""
🎮 FREE FIRE LIKE SUCCESS
────────────────────

👤 Free User
🎯 Player: {player_name}
🆔 UID: {uid}
🌍 Region: {region.upper()}

🎯 Target Likes: 50
✅ Likes Added By Bot: {likes_added}
📉 Failed to Send: {failed}

📊 Before Like: {likes_before}
📈 After Like: {likes_after}

━━━━━━━━━━━━━━━━━━━

🔥 Powered By PLUS OFFICIAL
"""

        bot.edit_message_text(
            final,
            message.chat.id,
            wait.message_id
        )

    except Exception as e:

        bot.edit_message_text(
            f"""
❌ API ERROR

━━━━━━━━━━━━━━━━━━━

{e}
""",
            message.chat.id,
            wait.message_id
        )

# =========================================================
#                      HELP CMD
# =========================================================

@bot.message_handler(commands=['help'])
def help_cmd(message):

    bot.send_message(
        message.chat.id,
        """
📖 HOW TO USE

━━━━━━━━━━━━━━━━━━━

1️⃣ SEND UID + REGION

EXAMPLE:
5513136279 ind

━━━━━━━━━━━━━━━━━━━

🌍 REGIONS:
ind
bd
sg
br
us

━━━━━━━━━━━━━━━━━━━

⚡ BOT FEATURES

✅ FORCE JOIN
✅ VERIFY BUTTON
✅ AUTO LIKE
✅ FAST RESPONSE
✅ ERROR HANDLER

━━━━━━━━━━━━━━━━━━━
"""
    )

# =========================================================
#                      RUN BOT
# =========================================================

print("🔥 BOT STARTED")

bot.infinity_polling()
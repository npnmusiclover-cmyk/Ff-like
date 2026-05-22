import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import re

# =========================================================
#                     BOT TOKEN
# =========================================================

BOT_TOKEN = "8496595814:AAGribEBb_Uoba0f6p8tw2Lz8WES5uOziB0"

bot = telebot.TeleBot(BOT_TOKEN)

# =========================================================
#                    CHANNELS
# =========================================================

CHANNEL_1 = "@inffo_01"
CHANNEL_2 = "@plus_official01"

# =========================================================
#                     API
# =========================================================

LIKE_API = "https://najmi-ob53-like-api.vercel.app/like"
API_KEY = "NJM"

# =========================================================
#                 WELCOME IMAGE
# =========================================================

WELCOME_IMAGE = "https://i.ibb.co/j9MRmhJT/colorful-welcome-lettering-modern-banner-invitation-1017-50216.jpg"

# =========================================================
#                 FORCE JOIN CHECK
# =========================================================

def is_joined(user_id):

    try:

        member1 = bot.get_chat_member(
            CHANNEL_1,
            user_id
        )

        member2 = bot.get_chat_member(
            CHANNEL_2,
            user_id
        )

        allowed = [
            "member",
            "administrator",
            "creator"
        ]

        if member1.status in allowed and member2.status in allowed:
            return True

    except:
        return False

    return False

# =========================================================
#                     START CMD
# =========================================================

@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    # =====================================================
    # USER NOT JOINED
    # =====================================================

    if not is_joined(user_id):

        markup = InlineKeyboardMarkup(row_width=1)

        btn1 = InlineKeyboardButton(
            "📢 JOIN CHANNEL 1",
            url="https://t.me/inffo_01"
        )

        btn2 = InlineKeyboardButton(
            "📢 JOIN CHANNEL 2",
            url="https://t.me/plus_official01"
        )

        btn3 = InlineKeyboardButton(
            "✅ VERIFY NOW",
            callback_data="verify"
        )

        markup.add(btn1, btn2, btn3)

        bot.send_photo(
            message.chat.id,
            WELCOME_IMAGE,
            caption="""
🔥 WELCOME TO FREE FIRE LIKE BOT 🔥

━━━━━━━━━━━━━━━━━━━

📌 HOW TO USE BOT

1️⃣ JOIN BOTH CHANNELS
2️⃣ CLICK VERIFY BUTTON
3️⃣ SEND UID + REGION

━━━━━━━━━━━━━━━━━━━

✅ EXAMPLE:

5513136279 ind

━━━━━━━━━━━━━━━━━━━

🌍 AVAILABLE REGIONS

🇮🇳 ind
🇧🇩 bd
🇸🇬 sg
🇧🇷 br
🇺🇸 us

━━━━━━━━━━━━━━━━━━━

⚡ INSTANT LIKE SYSTEM
💎 FAST SERVER
🎮 FREE SERVICE

━━━━━━━━━━━━━━━━━━━
""",
            reply_markup=markup
        )

        return

    # =====================================================
    # USER JOINED
    # =====================================================

    bot.send_photo(
        message.chat.id,
        WELCOME_IMAGE,
        caption="""
🎮 FREE FIRE LIKE BOT ACTIVE

━━━━━━━━━━━━━━━━━━━

📌 SEND UID + REGION

✅ EXAMPLE:
5513136279 ind

━━━━━━━━━━━━━━━━━━━

🌍 REGIONS:
ind
bd
sg
br
us

━━━━━━━━━━━━━━━━━━━

🔥 SEND NOW TO GET LIKES
"""
    )

# =========================================================
#                 VERIFY BUTTON FIXED
# =========================================================

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    if call.data == "verify":

        user_id = call.from_user.id

        # =================================================
        # CHECK JOIN
        # =================================================

        if not is_joined(user_id):

            bot.answer_callback_query(
                call.id,
                "❌ FIRST JOIN BOTH CHANNELS",
                show_alert=True
            )

            return

        # =================================================
        # SUCCESS VERIFY
        # =================================================

        bot.answer_callback_query(
            call.id,
            "✅ VERIFIED SUCCESSFULLY"
        )

        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption="""
✅ VERIFICATION SUCCESSFUL

━━━━━━━━━━━━━━━━━━━

🎮 NOW SEND UID + REGION

✅ EXAMPLE:
5513136279 ind

━━━━━━━━━━━━━━━━━━━

🔥 YOU CAN NOW USE BOT
"""
        )

# =========================================================
#                    LIKE SYSTEM
# =========================================================

@bot.message_handler(func=lambda message: True)
def like_system(message):

    user_id = message.from_user.id

    # =====================================================
    # FORCE JOIN CHECK
    # =====================================================

    if not is_joined(user_id):

        bot.send_message(
            message.chat.id,
            "❌ PLEASE JOIN CHANNELS FIRST\n\nUSE /start"
        )

        return

    text = message.text.strip()

    # =====================================================
    # UID FORMAT CHECK
    # =====================================================

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

✅ CORRECT FORMAT:

5513136279 ind

━━━━━━━━━━━━━━━━━━━
"""
        )

        return

    uid = match.group(1)
    region = match.group(2).lower()

    # =====================================================
    # WAIT MESSAGE
    # =====================================================

    wait = bot.send_message(
        message.chat.id,
        "⏳ PROCESSING LIKES..."
    )

    try:

        # =================================================
        # API REQUEST
        # =================================================

        url = (
            f"{LIKE_API}"
            f"?uid={uid}"
            f"&server_name={region}"
            f"&key={API_KEY}"
        )

        response = requests.get(url).json()

        # =================================================
        # JSON HANDLE
        # =================================================

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

        # =================================================
        # FINAL RESULT
        # =================================================

        final_text = f"""
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

🔥 POWERED BY PLUS OFFICIAL
"""

        bot.edit_message_text(
            final_text,
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
#                    HELP COMMAND
# =========================================================

@bot.message_handler(commands=['help'])
def help_command(message):

    bot.send_message(
        message.chat.id,
        """
📖 HOW TO USE BOT

━━━━━━━━━━━━━━━━━━━

1️⃣ JOIN CHANNELS

2️⃣ CLICK VERIFY

3️⃣ SEND UID + REGION

━━━━━━━━━━━━━━━━━━━

✅ EXAMPLE:

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
#                     BOT START
# =========================================================

print("🔥 BOT IS RUNNING")

bot.infinity_polling()

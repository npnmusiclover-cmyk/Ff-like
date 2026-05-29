import os
import json
import logging
import httpx
import asyncio

from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.constants import ParseMode

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)

# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")

print("BOT TOKEN =>", BOT_TOKEN)

ADMIN_ID = 8351165824

# API
API_URL = "https://aniketbramha.om-divine.workers.dev/?key=lundlo&num="

# CHANNELS
CHANNEL_1_ID = "@joinforfree110"
CHANNEL_1_LINK = "https://t.me/joinforfree110"
CHANNEL_1_NAME = "PLUS PRO"

CHANNEL_2_ID = "@plus_official01"
CHANNEL_2_LINK = "https://t.me/plus_official01"
CHANNEL_2_NAME = "PLUS OFFICIAL"

# =========================================================
# FILES
# =========================================================

USERS_FILE = "users.json"
BANNED_FILE = "banned.json"
HISTORY_FILE = "history.json"

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# =========================================================
# CREATE FILES
# =========================================================

DEFAULT_FILES = {
    USERS_FILE: {},
    BANNED_FILE: [],
    HISTORY_FILE: {}
}

for file, default in DEFAULT_FILES.items():

    if not os.path.exists(file):

        with open(file, "w") as f:
            json.dump(default, f)

# =========================================================
# JSON HELPERS
# =========================================================

def load_json(file, default):

    try:

        with open(file, "r") as f:
            return json.load(f)

    except:
        return default


def save_json(file, data):

    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# =========================================================
# DATABASE
# =========================================================

def load_users():
    return load_json(USERS_FILE, {})


def save_users(data):
    save_json(USERS_FILE, data)


def load_banned():
    return load_json(BANNED_FILE, [])


def save_banned(data):
    save_json(BANNED_FILE, data)


def load_history():
    return load_json(HISTORY_FILE, {})


def save_history(data):
    save_json(HISTORY_FILE, data)

# =========================================================
# ADMIN
# =========================================================

def is_admin(user_id):
    return int(user_id) == ADMIN_ID


def is_banned(user_id):

    banned = load_banned()

    return str(user_id) in [str(x) for x in banned]

# =========================================================
# REGISTER USER
# =========================================================

def register_user(user):

    users = load_users()

    uid = str(user.id)

    is_new = uid not in users

    users[uid] = {
        "id": user.id,
        "name": user.first_name,
        "username": user.username or "N/A",
        "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_users(users)

    return is_new

# =========================================================
# SEARCH HISTORY
# =========================================================

def log_search(user_id, number):

    history = load_history()

    uid = str(user_id)

    if uid not in history:
        history[uid] = []

    history[uid].append({
        "number": number,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    history[uid] = history[uid][-20:]

    save_history(history)

# =========================================================
# AUTO DELETE
# =========================================================

async def auto_delete_message(message, delay=60):

    await asyncio.sleep(delay)

    try:
        await message.delete()
    except:
        pass

# =========================================================
# FORCE JOIN
# =========================================================

async def is_member(bot, user_id, channel):

    try:

        member = await bot.get_chat_member(
            channel,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return False


def join_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"📢 {CHANNEL_1_NAME}",
                url=CHANNEL_1_LINK
            )
        ],
        [
            InlineKeyboardButton(
                f"📢 {CHANNEL_2_NAME}",
                url=CHANNEL_2_LINK
            )
        ],
        [
            InlineKeyboardButton(
                "✅ VERIFY NOW",
                callback_data="verify"
            )
        ]
    ])

async def check_join(update, context):

    user_id = update.effective_user.id

    if is_admin(user_id):
        return True

    if is_banned(user_id):

        await update.message.reply_text(
            "🚫 YOU ARE BANNED FROM USING THIS BOT"
        )

        return False

    bot = context.bot

    joined1 = await is_member(bot, user_id, CHANNEL_1_ID)
    joined2 = await is_member(bot, user_id, CHANNEL_2_ID)

    if joined1 and joined2:
        return True

    text = (
        "🔥 PREMIUM ACCESS REQUIRED 🔥\n\n"
        "JOIN BOTH CHANNELS TO USE THIS BOT"
    )

    await update.message.reply_text(
        text,
        reply_markup=join_keyboard()
    )

    return False

# =========================================================
# VERIFY
# =========================================================

async def verify(update, context):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    bot = context.bot

    joined1 = await is_member(bot, user_id, CHANNEL_1_ID)
    joined2 = await is_member(bot, user_id, CHANNEL_2_ID)

    if joined1 and joined2:

        await query.edit_message_text(
            "✅ VERIFIED SUCCESSFULLY\n\n"
            "USE:\n"
            "/num 9876543210"
        )

    else:

        await query.edit_message_text(
            "❌ JOIN BOTH CHANNELS FIRST",
            reply_markup=join_keyboard()
        )

# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_join(update, context):
        return

    user = update.effective_user

    is_new = register_user(user)

    if is_new:

        users = load_users()

        try:

            await context.bot.send_message(
                ADMIN_ID,
                f"🆕 NEW USER\n\n"
                f"👤 {user.first_name}\n"
                f"🆔 {user.id}\n"
                f"📊 USERS: {len(users)}"
            )

        except:
            pass

    text = (
        "🔍 *WELCOME TO PREMIUM NUMBER INFO BOT*\n\n"

        "📲 *AVAILABLE COMMANDS*\n\n"

        "`/start`\n"
        "`/help`\n"
        "`/num 9876543210`\n"
        "`/stats`\n"
        "`/users`\n"
        "`/bcast MESSAGE`\n\n"

        "📌 LONG PRESS COMMAND TO COPY\n\n"

        "🔥 FAST SEARCH SYSTEM"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔥 PLUS OFFICIAL 🔥",
                url=CHANNEL_2_LINK
            )
        ]
    ])

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )

# =========================================================
# HELP
# =========================================================

async def help_command(update, context):

    await update.message.reply_text(
        "/num 9876543210"
    )

# =========================================================
# NUMBER SEARCH
# =========================================================

async def num(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_join(update, context):
        return

    user = update.effective_user

    register_user(user)

    if not context.args:

        await update.message.reply_text(
            "❌ USE:\n/num 9876543210"
        )

        return

    number = context.args[0]

    if not number.isdigit():

        await update.message.reply_text(
            "❌ INVALID NUMBER"
        )

        return

    log_search(user.id, number)

    msg = await update.message.reply_text(
        "🔍 SEARCHING PREMIUM DATABASE..."
    )

    try:

        url = f"{API_URL}{number}"

        async with httpx.AsyncClient(timeout=30) as client:

            response = await client.get(url)

            if response.status_code != 200:

                await msg.edit_text(
                    f"❌ API ERROR\nSTATUS: {response.status_code}"
                )

                return

            try:

                data = response.json()

            except:

                await msg.edit_text(
                    "❌ INVALID API RESPONSE"
                )

                return

    except Exception as e:

        await msg.edit_text(
            f"❌ ERROR:\n{e}"
        )

        return

    print("API RESPONSE =", data)

    text = (
        "🔥 PREMIUM SEARCH RESULT 🔥\n\n"
        f"📱 NUMBER: {number}\n\n"
    )

    found = False

    # =====================================================
    # DICT SUPPORT
    # =====================================================

    if isinstance(data, dict):

        for key, value in data.items():

            if isinstance(value, dict):

                found = True

                text += (
                    "━━━━━━━━━━━━━━━━━━\n"
                    f"👤 NAME: {value.get('name', 'N/A')}\n"
                    f"👨 FATHER: {value.get('father name', 'N/A')}\n"
                    f"📱 MOBILE: {value.get('mobile', 'N/A')}\n"
                    f"📞 ALT: {value.get('alternative mobile', 'N/A')}\n"
                    f"📡 SIM: {value.get('circle/sim', 'N/A')}\n"
                    f"🏠 ADDRESS: {value.get('address', 'N/A')}\n"
                    f"🪪 ID: {value.get('id number', 'N/A')}\n"
                    f"📧 EMAIL: {value.get('mail', 'N/A')}\n\n"
                )

        # DIRECT DATA
        if not found:

            found = True

            for key, value in data.items():

                text += f"🔹 {key} : {value}\n"

    # =====================================================
    # LIST SUPPORT
    # =====================================================

    elif isinstance(data, list):

        for item in data:

            if isinstance(item, dict):

                found = True

                text += (
                    "━━━━━━━━━━━━━━━━━━\n"
                    f"👤 NAME: {item.get('name', 'N/A')}\n"
                    f"👨 FATHER: {item.get('father name', 'N/A')}\n"
                    f"📱 MOBILE: {item.get('mobile', 'N/A')}\n"
                    f"📞 ALT: {item.get('alternative mobile', 'N/A')}\n"
                    f"📡 SIM: {item.get('circle/sim', 'N/A')}\n"
                    f"🏠 ADDRESS: {item.get('address', 'N/A')}\n"
                    f"🪪 ID: {item.get('id number', 'N/A')}\n"
                    f"📧 EMAIL: {item.get('mail', 'N/A')}\n\n"
                )

    if not found:

        text += "❌ NO VALID DATA FOUND"

    if len(text) > 4000:
        text = text[:4000]

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔥 PLUS OFFICIAL 🔥",
                url=CHANNEL_2_LINK
            )
        ]
    ])

    result_message = await msg.edit_text(
        text,
        reply_markup=keyboard
    )

    # =====================================================
    # AUTO DELETE IN 60 SECONDS
    # =====================================================

    asyncio.create_task(
        auto_delete_message(result_message, 60)
    )

# =========================================================
# USERS
# =========================================================

async def users(update, context):

    if not is_admin(update.effective_user.id):
        return

    users_data = load_users()

    text = f"👥 TOTAL USERS: {len(users_data)}"

    await update.message.reply_text(text)

# =========================================================
# BROADCAST
# =========================================================

async def bcast(update, context):

    if not is_admin(update.effective_user.id):
        return

    if not context.args:

        await update.message.reply_text(
            "USE:\n/bcast MESSAGE"
        )

        return

    message = " ".join(context.args)

    users_data = load_users()

    sent = 0
    failed = 0

    status = await update.message.reply_text(
        "📢 BROADCAST STARTED..."
    )

    for uid in list(users_data.keys()):

        try:

            await context.bot.send_message(
                int(uid),
                f"📢 BROADCAST MESSAGE\n\n{message}"
            )

            sent += 1

        except Exception as e:

            print(e)

            failed += 1

    await status.edit_text(
        f"✅ COMPLETE\n\n"
        f"📨 SENT: {sent}\n"
        f"❌ FAILED: {failed}"
    )

# =========================================================
# BAN
# =========================================================

async def ban(update, context):

    if not is_admin(update.effective_user.id):
        return

    uid = context.args[0]

    banned = load_banned()

    if uid not in banned:

        banned.append(uid)

        save_banned(banned)

    await update.message.reply_text(
        f"🚫 BANNED:\n{uid}"
    )

# =========================================================
# UNBAN
# =========================================================

async def unban(update, context):

    if not is_admin(update.effective_user.id):
        return

    uid = context.args[0]

    banned = load_banned()

    if uid in banned:

        banned.remove(uid)

        save_banned(banned)

    await update.message.reply_text(
        f"✅ UNBANNED:\n{uid}"
    )

# =========================================================
# STATS
# =========================================================

async def stats(update, context):

    if not is_admin(update.effective_user.id):
        return

    users_data = load_users()

    history = load_history()

    total_searches = sum(
        len(v) for v in history.values()
    )

    text = (
        "📊 BOT STATS\n\n"
        f"👥 USERS: {len(users_data)}\n"
        f"🔍 SEARCHES: {total_searches}"
    )

    await update.message.reply_text(text)

# =========================================================
# MAIN
# =========================================================

def main():

    if not BOT_TOKEN:

        print("❌ BOT_TOKEN NOT FOUND")

        return

    print("✅ BOT STARTED")

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    # USER COMMANDS
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("num", num))

    # ADMIN COMMANDS
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("bcast", bcast))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("stats", stats))

    # CALLBACK
    app.add_handler(
        CallbackQueryHandler(
            verify,
            pattern="^verify$"
        )
    )

    app.run_polling(
        drop_pending_updates=True
    )

# =========================================================
# START BOT
# =========================================================

if __name__ == "__main__":
    main()

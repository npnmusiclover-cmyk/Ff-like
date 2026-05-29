import os
import json
import logging
import httpx
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)

# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")

API_URL = "https://numinfo.eu.cc/api/check"

ADMIN_ID = 8351165824

CHANNEL_1_ID = "@joinforfree110"
CHANNEL_1_LINK = "https://t.me/joinforfree110"
CHANNEL_1_NAME = "PLUSOFFICIAL"

CHANNEL_2_ID = "@plus_official01"
CHANNEL_2_LINK = "https://t.me/plus_official01"
CHANNEL_2_NAME = "PLUS OFFICIAL"

# =========================================================
# FILES
# =========================================================

USERS_FILE = "users.json"
BANNED_FILE = "banned.json"
PROTECTED_FILE = "protected.json"
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
    PROTECTED_FILE: [],
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


def load_protected():
    return load_json(PROTECTED_FILE, [])


def save_protected(data):
    save_json(PROTECTED_FILE, data)


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

        if update.message:
            await update.message.reply_text(
                "🚫 YOU ARE BANNED FROM USING THIS BOT"
            )

        return False

    bot = context.bot

    joined1 = await is_member(
        bot,
        user_id,
        CHANNEL_1_ID
    )

    joined2 = await is_member(
        bot,
        user_id,
        CHANNEL_2_ID
    )

    if joined1 and joined2:
        return True

    text = (
        "🔥 PREMIUM ACCESS REQUIRED 🔥\n\n"
        "JOIN BOTH CHANNELS TO USE THIS BOT\n\n"
        f"📢 {CHANNEL_1_NAME}\n"
        f"📢 {CHANNEL_2_NAME}\n\n"
        "AFTER JOIN CLICK VERIFY BUTTON"
    )

    if update.message:
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

    joined1 = await is_member(
        bot,
        user_id,
        CHANNEL_1_ID
    )

    joined2 = await is_member(
        bot,
        user_id,
        CHANNEL_2_ID
    )

    if joined1 and joined2:

        text = (
            "✅ VERIFIED SUCCESSFULLY\n\n"
            "🔍 USE:\n"
            "/num 9876543210\n\n"
            "🚀 PREMIUM ACCESS ENABLED"
        )

        await query.edit_message_text(text)

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
                f"👤 NAME: {user.first_name}\n"
                f"🆔 ID: {user.id}\n"
                f"📊 TOTAL USERS: {len(users)}"
            )

        except:
            pass

    text = (
        "🔥 PREMIUM NUMBER INFO BOT 🔥\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "⚡ FAST SEARCH\n"
        "📡 LIVE DATABASE\n"
        "🔍 PREMIUM RESULTS\n"
        "👥 GROUP SUPPORT ENABLED\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "📲 COMMAND:\n"
        "/num 9876543210\n\n"
        "🚀 POWERED BY PLUS OFFICIAL"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 JOIN CHANNEL",
                url=CHANNEL_1_LINK
            )
        ]
    ])

    await update.message.reply_text(
        text,
        reply_markup=keyboard
    )

# =========================================================
# HELP
# =========================================================

async def help_command(update, context):

    text = (
        "📚 AVAILABLE COMMANDS\n\n"
        "/start - START BOT\n"
        "/help - HELP MENU\n"
        "/num <number> - SEARCH NUMBER\n\n"
        "📲 EXAMPLE:\n"
        "/num 9876543210"
    )

    await update.message.reply_text(text)

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

    protected = load_protected()

    if number in protected:

        await update.message.reply_text(
            "🔒 THIS NUMBER IS PROTECTED"
        )

        return

    log_search(user.id, number)

    msg = await update.message.reply_text(
        "🔍 SEARCHING DATABASE..."
    )

    try:

        params = {
            "apikey": API_KEY,
            "number": number
        }

        async with httpx.AsyncClient(timeout=20) as client:

            response = await client.get(
                API_URL,
                params=params
            )

            data = response.json()

    except Exception as e:

        await msg.edit_text(
            f"❌ ERROR:\n{e}"
        )

        return

    results = []

    for key, value in data.items():

        if key == "credit":
            continue

        if isinstance(value, dict):
            results.append(value)

    if not results:

        await msg.edit_text(
            "❌ NO DATA FOUND"
        )

        return

    text = (
        f"🔥 PREMIUM SEARCH RESULT 🔥\n\n"
        f"📱 NUMBER: {number}\n"
        f"📊 RESULTS: {len(results)}\n\n"
    )

    for i, item in enumerate(results, start=1):

        text += (
            "━━━━━━━━━━━━━━━━━━━\n"
            f"📌 RESULT #{i}\n\n"
            f"👤 NAME: {item.get('name', 'N/A')}\n"
            f"👨 FATHER: {item.get('father name', 'N/A')}\n"
            f"📱 MOBILE: {item.get('mobile', 'N/A')}\n"
            f"📞 ALT: {item.get('alternative mobile', 'N/A')}\n"
            f"📡 SIM: {item.get('circle/sim', 'N/A')}\n"
            f"🏠 ADDRESS: {item.get('address', 'N/A')}\n"
            f"🪪 ID: {item.get('id number', 'N/A')}\n"
            f"📧 EMAIL: {item.get('mail', 'N/A')}\n\n"
        )

    if len(text) > 4000:
        text = text[:4000]

    await msg.edit_text(text)

# =========================================================
# USERS
# =========================================================

async def users(update, context):

    if not is_admin(update.effective_user.id):
        return

    users_data = load_users()

    text = f"👥 TOTAL USERS: {len(users_data)}\n\n"

    for uid, info in users_data.items():

        text += (
            f"👤 {info['name']}\n"
            f"🆔 {uid}\n"
            f"🔗 @{info['username']}\n\n"
        )

    if len(text) > 4000:
        text = text[:4000]

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

    for uid in users_data:

        try:

            await context.bot.send_message(
                int(uid),
                f"📢 BROADCAST MESSAGE\n\n{message}"
            )

            sent += 1

        except:
            failed += 1

    await status.edit_text(
        f"✅ BROADCAST COMPLETE\n\n"
        f"📨 SENT: {sent}\n"
        f"❌ FAILED: {failed}"
    )

# =========================================================
# BAN USER
# =========================================================

async def ban(update, context):

    if not is_admin(update.effective_user.id):
        return

    if not context.args:

        await update.message.reply_text(
            "USE:\n/ban USER_ID"
        )

        return

    uid = context.args[0]

    banned = load_banned()

    if uid in banned:

        await update.message.reply_text(
            "USER ALREADY BANNED"
        )

        return

    banned.append(uid)

    save_banned(banned)

    await update.message.reply_text(
        f"🚫 USER BANNED:\n{uid}"
    )

# =========================================================
# UNBAN USER
# =========================================================

async def unban(update, context):

    if not is_admin(update.effective_user.id):
        return

    if not context.args:

        await update.message.reply_text(
            "USE:\n/unban USER_ID"
        )

        return

    uid = context.args[0]

    banned = load_banned()

    if uid not in banned:

        await update.message.reply_text(
            "USER NOT BANNED"
        )

        return

    banned.remove(uid)

    save_banned(banned)

    await update.message.reply_text(
        f"✅ USER UNBANNED:\n{uid}"
    )

# =========================================================
# STATS
# =========================================================

async def stats(update, context):

    if not is_admin(update.effective_user.id):
        return

    users_data = load_users()
    banned = load_banned()
    protected = load_protected()
    history = load_history()

    total_searches = sum(
        len(v) for v in history.values()
    )

    text = (
        "📊 BOT STATISTICS\n\n"
        f"👥 USERS: {len(users_data)}\n"
        f"🚫 BANNED: {len(banned)}\n"
        f"🔒 PROTECTED: {len(protected)}\n"
        f"🔍 SEARCHES: {total_searches}"
    )

    await update.message.reply_text(text)

# =========================================================
# MAIN
# =========================================================

def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN NOT FOUND")

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

    logger.info("BOT STARTED SUCCESSFULLY")

    app.run_polling(
        drop_pending_updates=True
    )

# =========================================================
# START BOT
# =========================================================

if __name__ == "__main__":
    main()

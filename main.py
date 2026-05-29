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

BOT_TOKEN = "8987520659:AAGWFLIGwK5ZV9DKZs8Maulq6Bc_w4zRKR0"

# YOUR API
API_URL = "https://aniketbramha.om-divine.workers.dev"

API_KEY = "lundlo"

ADMIN_ID = 8351165824

# =========================================================
# FORCE JOIN CHANNELS
# =========================================================

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

FILES = {
    USERS_FILE: {},
    BANNED_FILE: [],
    HISTORY_FILE: {}
}

for file, default in FILES.items():

    if not os.path.exists(file):

        with open(file, "w") as f:
            json.dump(default, f)

# =========================================================
# JSON FUNCTIONS
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

    new = uid not in users

    users[uid] = {
        "name": user.first_name,
        "username": user.username or "N/A",
        "joined": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }

    save_users(users)

    return new

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
        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    })

    history[uid] = history[uid][-20:]

    save_history(history)

# =========================================================
# FORCE JOIN
# =========================================================

async def is_member(bot, user_id, channel):

    try:

        member = await bot.get_chat_member(channel, user_id)

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

        await query.edit_message_text(
            "✅ VERIFIED SUCCESSFULLY\n\n"
            "📲 USE:\n"
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

        try:

            users = load_users()

            await context.bot.send_message(
                ADMIN_ID,
                f"🆕 NEW USER\n\n"
                f"👤 NAME: {user.first_name}\n"
                f"🆔 ID: {user.id}\n"
                f"📊 USERS: {len(users)}"
            )

        except:
            pass

    text = (
        "🔍 *WELCOME TO PREMIUM NUMBER INFO BOT* 🔍\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ FAST & PREMIUM SEARCH\n"
        "📡 LIVE DATABASE ACCESS\n"
        "🔒 SECURE SYSTEM\n"
        "👥 GROUP SUPPORTED\n"
        "🚀 HIGH SPEED RESULTS\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📲 *AVAILABLE COMMANDS*\n\n"
        "🔹 `/start` - Start Bot\n"
        "🔹 `/help` - Help Menu\n"
        "🔹 `/num <number>` - Search Number\n"
        "🔹 `/stats` - Bot Stats (Admin)\n"
        "🔹 `/users` - All Users (Admin)\n"
        "🔹 `/bcast` - Broadcast (Admin)\n"
        "🔹 `/ban` - Ban User (Admin)\n"
        "🔹 `/unban` - Unban User (Admin)\n\n"
        "📌 *EXAMPLE:*\n"
        "`/num 9876543210`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 *FEATURES*\n"
        "• Full Name\n"
        "• Father Name\n"
        "• Mobile Number\n"
        "• Alternative Number\n"
        "• Address Details\n"
        "• SIM / Circle Info\n"
        "• Email Information\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 *POWERED BY* [PLUS OFFICIAL](https://t.me/plus_official01)"
    )

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "📢 JOIN CHANNEL",
                url=CHANNEL_1_LINK
            )
        ],

        [
            InlineKeyboardButton(
                "🚀 POWERED BY PLUS OFFICIAL",
                url="https://t.me/plus_official01"
            )
        ]
    ])

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard
    )

# =========================================================
# HELP
# =========================================================

async def help_command(update, context):

    text = (
        "📚 *HELP MENU*\n\n"
        "🔹 `/num 9876543210`\n"
        "Search any mobile number.\n\n"
        "🔹 `/start`\n"
        "Start the bot.\n\n"
        "🔹 `/help`\n"
        "Open help menu."
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN
    )

# =========================================================
# NUMBER SEARCH
# =========================================================

async def num(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_join(update, context):
        return

    if not context.args:

        await update.message.reply_text(
            "❌ USE:\n`/num 9876543210`",
            parse_mode=ParseMode.MARKDOWN
        )

        return

    number = context.args[0]

    if not number.isdigit():

        await update.message.reply_text(
            "❌ INVALID NUMBER"
        )

        return

    msg = await update.message.reply_text(
        "🔍 SEARCHING DATABASE..."
    )

    try:

        url = f"{API_URL}/?key={API_KEY}&num={number}"

        async with httpx.AsyncClient(timeout=30) as client:

            response = await client.get(url)

        if response.status_code != 200:

            await msg.edit_text(
                f"❌ API ERROR\n\nSTATUS CODE: {response.status_code}"
            )

            return

        try:
            data = response.json()
        except:

            await msg.edit_text(
                "❌ INVALID API RESPONSE"
            )

            return

        if not data or not isinstance(data, list):

            await msg.edit_text(
                "❌ NO VALID DATA FOUND"
            )

            return

        item = data[0]

        name = item.get("NAME", "N/A")
        fname = item.get("fname", "N/A")
        address = item.get("ADDRESS", "N/A")
        circle = item.get("circle", "N/A")
        mobile = item.get("MOBILE", "N/A")
        alt = item.get("alt", "N/A")
        idno = item.get("id", "N/A")
        email = item.get("email", "N/A")

        text = (
            "🔥 *PREMIUM SEARCH RESULT* 🔥\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📱 *NUMBER:* `{number}`\n"
            f"👤 *NAME:* `{name}`\n"
            f"👨 *FATHER:* `{fname}`\n"
            f"📞 *MOBILE:* `{mobile}`\n"
            f"☎️ *ALT NUMBER:* `{alt}`\n"
            f"📡 *SIM INFO:* `{circle}`\n"
            f"🏠 *ADDRESS:* `{address}`\n"
            f"🪪 *ID:* `{idno}`\n"
            f"📧 *EMAIL:* `{email}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🚀 *POWERED BY PLUS OFFICIAL*"
        )

        log_search(update.effective_user.id, number)

        await msg.edit_text(
            text,
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:

        await msg.edit_text(
            f"❌ ERROR:\n{e}"
        )

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
            "USE:\n/bcast YOUR_MESSAGE"
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
        f"✅ BROADCAST COMPLETED\n\n"
        f"📨 SENT: {sent}\n"
        f"❌ FAILED: {failed}"
    )

# =========================================================
# BAN
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

    if uid not in banned:

        banned.append(uid)

        save_banned(banned)

    await update.message.reply_text(
        f"🚫 USER BANNED\n\nID: {uid}"
    )

# =========================================================
# UNBAN
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

    if uid in banned:

        banned.remove(uid)

        save_banned(banned)

    await update.message.reply_text(
        f"✅ USER UNBANNED\n\nID: {uid}"
    )

# =========================================================
# STATS
# =========================================================

async def stats(update, context):

    if not is_admin(update.effective_user.id):
        return

    users_data = load_users()
    banned = load_banned()
    history = load_history()

    searches = sum(
        len(v) for v in history.values()
    )

    text = (
        "📊 BOT STATISTICS\n\n"
        f"👥 USERS: {len(users_data)}\n"
        f"🚫 BANNED: {len(banned)}\n"
        f"🔍 SEARCHES: {searches}"
    )

    await update.message.reply_text(text)

# =========================================================
# MAIN
# =========================================================

def main():

    if not BOT_TOKEN:
        raise ValueError("BOT TOKEN NOT FOUND")

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    # USER
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("num", num))

    # ADMIN
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("bcast", bcast))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("stats", stats))

    # VERIFY
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

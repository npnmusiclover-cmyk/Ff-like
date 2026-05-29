import logging
import json
import os
import httpx
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv(8987520659:AAGWFLIGwK5ZV9DKZs8Maulq6Bc_w4zRKR0")
API_KEY = os.getenv("https://aniketbramha.om-divine.workers.dev/?key=lundlo&num=")

API_URL = "https://numinfo.eu.cc/api/check"

ADMIN_ID = 8351165824

CHANNEL_1_ID = "@joinforfree110"
CHANNEL_1_LINK = "https://t.me/joinforfree110"
CHANNEL_1_NAME = "PLUSOFFICIAL"

CHANNEL_2_ID = "@plus_official01"
CHANNEL_2_LINK = "https://t.me/plus_official01"
CHANNEL_2_NAME = "PLUS OFFICIAL"

USERS_FILE = "users.json"
PROTECTED_FILE = "protected.json"
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
# AUTO CREATE FILES
# =========================================================


def ensure_file(file_name, default_data):
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            json.dump(default_data, f)


ensure_file(USERS_FILE, {})
ensure_file(PROTECTED_FILE, [])
ensure_file(BANNED_FILE, [])
ensure_file(HISTORY_FILE, {})

# =========================================================
# JSON HELPERS
# =========================================================


def load_json(file_name, default):
    try:
        with open(file_name, "r") as f:
            return json.load(f)
    except:
        return default


def save_json(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=2)


# =========================================================
# DATA HELPERS
# =========================================================


def load_users():
    return load_json(USERS_FILE, {})


def save_users(data):
    save_json(USERS_FILE, data)


def load_protected():
    return load_json(PROTECTED_FILE, [])


def save_protected(data):
    save_json(PROTECTED_FILE, data)


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
# USER REGISTER
# =========================================================


def register_user(user):

    users = load_users()

    uid = str(user.id)

    new_user = uid not in users

    users[uid] = {
        "id": user.id,
        "username": user.username or "N/A",
        "first_name": user.first_name or "N/A",
        "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_users(users)

    return new_user

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
                f"➕ {CHANNEL_1_NAME}",
                url=CHANNEL_1_LINK
            ),
            InlineKeyboardButton(
                f"➕ {CHANNEL_2_NAME}",
                url=CHANNEL_2_LINK
            )
        ],
        [
            InlineKeyboardButton(
                "✅ VERIFY",
                callback_data="verify_join"
            )
        ]
    ])


async def check_force_join(update, context):

    user_id = update.effective_user.id

    if is_admin(user_id):
        return True

    if is_banned(user_id):

        if update.message:
            await update.message.reply_text(
                "🚫 You are banned from this bot."
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
        "❌ JOIN BOTH CHANNELS FIRST\n\n"
        f"📢 {CHANNEL_1_NAME}\n"
        f"📢 {CHANNEL_2_NAME}\n\n"
        "Then click VERIFY."
    )

    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=join_keyboard()
        )

    return False

# =========================================================
# VERIFY BUTTON
# =========================================================


async def verify_callback(update, context):

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
            "Now use:\n"
            "/num 9876543210"
        )

    else:

        await query.edit_message_text(
            "❌ You still haven't joined both channels.",
            reply_markup=join_keyboard()
        )

# =========================================================
# START
# =========================================================


async def start(update: Update, context):

    if not await check_force_join(update, context):
        return

    user = update.effective_user

    new_user = register_user(user)

    if new_user:

        users = load_users()

        try:

            await context.bot.send_message(
                ADMIN_ID,
                f"🆕 NEW USER\n\n"
                f"👤 Name: {user.first_name}\n"
                f"🆔 ID: {user.id}\n"
                f"📊 Users: {len(users)}"
            )

        except Exception as e:
            logger.warning(e)

    text = (
        "🔍 NUMBER INFO BOT\n\n"
        "━━━━━━━━━━━━━━━\n"
        "USE:\n"
        "/num 9876543210\n\n"
        "━━━━━━━━━━━━━━━\n"
        "GROUP SUPPORT ENABLED ✅"
    )

    await update.message.reply_text(text)

# =========================================================
# HELP
# =========================================================


async def help_command(update, context):

    if not await check_force_join(update, context):
        return

    text = (
        "/start - Start Bot\n"
        "/help - Help Menu\n"
        "/num <number> - Search Number"
    )

    await update.message.reply_text(text)

# =========================================================
# NUMBER SEARCH
# =========================================================


async def num_command(update, context):

    if not await check_force_join(update, context):
        return

    user = update.effective_user

    register_user(user)

    if not context.args:

        await update.message.reply_text(
            "USAGE:\n"
            "/num 9876543210"
        )

        return

    number = context.args[0].strip()

    if not number.isdigit():

        await update.message.reply_text(
            "❌ DIGITS ONLY"
        )

        return

    if len(number) < 7 or len(number) > 15:

        await update.message.reply_text(
            "❌ INVALID NUMBER"
        )

        return

    protected = load_protected()

    if number in protected:

        await update.message.reply_text(
            "🔒 NUMBER PROTECTED"
        )

        return

    log_search(user.id, number)

    searching = await update.message.reply_text(
        "🔍 SEARCHING..."
    )

    try:

        params = {
            "apikey": API_KEY,
            "number": number
        }

        async with httpx.AsyncClient(
            timeout=20
        ) as client:

            response = await client.get(
                API_URL,
                params=params
            )

            response.raise_for_status()

            data = response.json()

    except httpx.TimeoutException:

        await searching.edit_text(
            "❌ REQUEST TIMEOUT"
        )

        return

    except Exception as e:

        await searching.edit_text(
            f"❌ ERROR:\n{e}"
        )

        return

    entries = [
        value for key, value in data.items()
        if key != "credit"
        and isinstance(value, dict)
    ]

    if not entries:

        await searching.edit_text(
            "❌ NO DATA FOUND"
        )

        return

    text = (
        f"🔎 NUMBER: {number}\n"
        f"📊 RESULTS: {len(entries)}\n\n"
    )

    for i, entry in enumerate(entries, start=1):

        name = entry.get("name", "N/A")
        father = entry.get("father name", "N/A")
        mobile = entry.get("mobile", "N/A")
        sim = entry.get("circle/sim", "N/A")
        address = entry.get("address", "N/A")
        mail = entry.get("mail", "N/A")
        alt = entry.get("alternative mobile", "N/A")
        idnum = entry.get("id number", "N/A")

        text += (
            f"━━━━━━━━━━━━━━━\n"
            f"📌 RESULT #{i}\n\n"
            f"👤 NAME: {name}\n"
            f"👨 FATHER: {father}\n"
            f"📱 MOBILE: {mobile}\n"
            f"📞 ALT: {alt}\n"
            f"📡 SIM: {sim}\n"
            f"🏠 ADDRESS: {address}\n"
            f"🪪 ID: {idnum}\n"
            f"📧 EMAIL: {mail}\n\n"
        )

    if len(text) > 4096:
        text = text[:4000]

    await searching.edit_text(text)

# =========================================================
# USERS
# =========================================================


async def users_command(update, context):

    if not is_admin(update.effective_user.id):
        return

    users = load_users()

    text = f"👥 TOTAL USERS: {len(users)}\n\n"

    for uid, info in users.items():

        text += (
            f"👤 {info['first_name']}\n"
            f"🆔 {uid}\n"
            f"🔗 @{info['username']}\n\n"
        )

    if len(text) > 4096:
        text = text[:4000]

    await update.message.reply_text(text)

# =========================================================
# BROADCAST
# =========================================================


async def broadcast(update, context):

    if not is_admin(update.effective_user.id):
        return

    if not context.args:

        await update.message.reply_text(
            "USAGE:\n"
            "/bcast message"
        )

        return

    message = " ".join(context.args)

    users = load_users()

    sent = 0

    failed = 0

    for uid in users:

        try:

            await context.bot.send_message(
                int(uid),
                f"📢 BROADCAST\n\n{message}"
            )

            sent += 1

        except:

            failed += 1

    await update.message.reply_text(
        f"✅ DONE\n\n"
        f"📨 SENT: {sent}\n"
        f"❌ FAILED: {failed}"
    )

# =========================================================
# BAN
# =========================================================


async def ban_user(update, context):

    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        return

    uid = context.args[0]

    banned = load_banned()

    if uid not in banned:
        banned.append(uid)

    save_banned(banned)

    await update.message.reply_text(
        f"🚫 BANNED {uid}"
    )


async def unban_user(update, context):

    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        return

    uid = context.args[0]

    banned = load_banned()

    banned = [x for x in banned if str(x) != str(uid)]

    save_banned(banned)

    await update.message.reply_text(
        f"✅ UNBANNED {uid}"
    )

# =========================================================
# MAIN
# =========================================================


def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN missing")

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    # USER
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("num", num_command))

    # ADMIN
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("bcast", broadcast))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))

    # CALLBACK
    app.add_handler(
        CallbackQueryHandler(
            verify_callback,
            pattern="^verify_join$"
        )
    )

    logger.info("BOT STARTED")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()

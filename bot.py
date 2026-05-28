import logging
import json
import os
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# ===================== CONFIGURATION =====================

BOT_TOKEN = os.getenv("8661261432:AAEvxdh7IWtt3j6z765_OphNtZZTsFsyiCw")

API_KEY = "SupportMe"
API_URL = "https://numinfo.eu.cc/api/check"

# Admin User ID
ADMIN_ID = 8351165824

# Force Join Channels
CHANNEL_1_ID = "@plus_official01"
CHANNEL_1_LINK = "https://t.me/plus_official01"
CHANNEL_1_NAME = "PLUS PRO"

CHANNEL_2_ID = "@inffo_01"
CHANNEL_2_LINK = "https://t.me/inffo_01"
CHANNEL_2_NAME = "INFFO_01"

# Data files
USERS_FILE = "users.json"
PROTECTED_FILE = "protected.json"
BANNED_FILE = "banned.json"
HISTORY_FILE = "history.json"

# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# ===================== DATA HELPERS =====================

def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users: dict) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def load_protected() -> list:
    if os.path.exists(PROTECTED_FILE):
        with open(PROTECTED_FILE, "r") as f:
            return json.load(f)
    return []


def save_protected(protected: list) -> None:
    with open(PROTECTED_FILE, "w") as f:
        json.dump(protected, f, indent=2)


def load_banned() -> list:
    if os.path.exists(BANNED_FILE):
        with open(BANNED_FILE, "r") as f:
            return json.load(f)
    return []


def save_banned(banned: list) -> None:
    with open(BANNED_FILE, "w") as f:
        json.dump(banned, f, indent=2)


def load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}


def save_history(history: dict) -> None:
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def log_search(user_id: int, number: str) -> None:
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


def register_user(user) -> bool:

    users = load_users()

    uid = str(user.id)

    is_new = uid not in users

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    users[uid] = {
        "id": user.id,
        "username": user.username or "N/A",
        "first_name": user.first_name or "N/A",
        "joined": users[uid].get("joined", now) if uid in users else now,
    }

    save_users(users)

    return is_new


# ===================== ADMIN & BAN CHECK =====================

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def is_banned(user_id: int) -> bool:
    return str(user_id) in [str(b) for b in load_banned()]


# ===================== FORCE JOIN =====================

async def is_member(bot, user_id: int, channel: str) -> bool:
    try:
        member = await bot.get_chat_member(channel, user_id)

        return member.status in (
            "member",
            "administrator",
            "creator"
        )

    except Exception as e:
        logger.error(e)
        return False


def join_keyboard() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"➕ Join {CHANNEL_1_NAME}",
                url=CHANNEL_1_LINK
            )
        ],
        [
            InlineKeyboardButton(
                f"➕ Join {CHANNEL_2_NAME}",
                url=CHANNEL_2_LINK
            )
        ],
        [
            InlineKeyboardButton(
                "✅ VERIFY NOW",
                callback_data="verify_join"
            )
        ]
    ])


def result_keyboard() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"📢 {CHANNEL_1_NAME}",
                url=CHANNEL_1_LINK
            ),

            InlineKeyboardButton(
                f"📢 {CHANNEL_2_NAME}",
                url=CHANNEL_2_LINK
            ),
        ]
    ])


async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:

    user_id = update.effective_user.id

    if is_banned(user_id) and not is_admin(user_id):

        await update.message.reply_text(
            "🚫 You are banned from using this bot."
        )

        return False

    if is_admin(user_id):
        return True

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

    await update.message.reply_text(
        "⚠️ Please join both channels first.",
        reply_markup=join_keyboard()
    )

    return False


async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
            "✅ VERIFIED SUCCESSFULLY\n\nNow use:\n/num 9876543210"
        )

    else:

        await query.answer(
            "❌ Join both channels first.",
            show_alert=True
        )


# ===================== START =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_force_join(update, context):
        return

    user = update.effective_user

    is_new = register_user(user)

    if is_new:

        users = load_users()

        total = len(users)

        username_display = (
            f"@{user.username}"
            if user.username else "No Username"
        )

        notify_msg = (
            f"🆕 New User Joined!\n\n"
            f"👤 Name: {user.first_name}\n"
            f"🔗 Username: {username_display}\n"
            f"🆔 User ID: {user.id}\n"
            f"📊 Total Users: {total}"
        )

        try:

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=notify_msg
            )

        except Exception as e:
            logger.warning(e)

    text = f"""
🔥 WELCOME TO NUMBER INFO BOT 🔥

👋 Hello {user.first_name}

━━━━━━━━━━━━━━━━━━

📌 HOW TO USE

/num 9876543210

━━━━━━━━━━━━━━━━━━

✅ FEATURES

• Full Name
• Father Name
• Address
• SIM Info
• Email
• ID Number

━━━━━━━━━━━━━━━━━━

⚡ Powered By PLUS PRO
"""

    await update.message.reply_text(text)


# ===================== HELP =====================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_force_join(update, context):
        return

    text = """
📖 AVAILABLE COMMANDS

/start - Start Bot

/num 9876543210
Search any number

/help - Help Menu
"""

    await update.message.reply_text(text)


# ===================== NUM SEARCH =====================

async def num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_force_join(update, context):
        return

    user = update.effective_user

    register_user(user)

    if not context.args:

        await update.message.reply_text(
            "⚠️ Usage:\n/num 9876543210"
        )

        return

    mobile_number = context.args[0].strip()

    if not mobile_number.isdigit():

        await update.message.reply_text(
            "❌ Digits only."
        )

        return

    protected = load_protected()

    if mobile_number in protected:

        await update.message.reply_text(
            "🔒 This number is protected."
        )

        return

    log_search(user.id, mobile_number)

    searching_msg = await update.message.reply_text(
        "🔍 Searching..."
    )

    try:

        params = {
            "apikey": API_KEY,
            "number": mobile_number
        }

        async with httpx.AsyncClient(timeout=20) as client:

            response = await client.get(
                API_URL,
                params=params
            )

            response.raise_for_status()

            data = response.json()

    except Exception as e:

        await searching_msg.edit_text(
            f"❌ Error:\n{e}"
        )

        return

    entries = [
        val for key, val in data.items()
        if key != "credit" and isinstance(val, dict)
    ]

    if not entries:

        await searching_msg.edit_text(
            "❌ No data found."
        )

        return

    all_blocks = []

    header = (
        f"🔎 Number: {mobile_number}\n"
        f"📊 Total Results: {len(entries)}\n"
    )

    all_blocks.append(header)

    for i, entry in enumerate(entries, start=1):

        all_blocks.append(
            format_entry(i, entry)
        )

    full_message = "\n".join(all_blocks)

    chunks = split_message(full_message, 4000)

    try:
        await searching_msg.delete()
    except:
        pass

    for idx, chunk in enumerate(chunks):

        kb = result_keyboard() if idx == len(chunks) - 1 else None

        await update.message.reply_text(
            chunk,
            reply_markup=kb
        )


# ===================== ADMIN COMMANDS =====================

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):

        await update.message.reply_text(
            "❌ Admin only."
        )

        return

    users = load_users()

    protected = load_protected()

    banned = load_banned()

    history = load_history()

    total_searches = sum(
        len(v) for v in history.values()
    )

    text = (
        f"📊 BOT STATS\n\n"
        f"👥 Users: {len(users)}\n"
        f"🔒 Protected: {len(protected)}\n"
        f"🚫 Banned: {len(banned)}\n"
        f"🔍 Searches: {total_searches}"
    )

    await update.message.reply_text(text)


# ===================== HELPERS =====================

def clean(value) -> str:

    if value is None:
        return "N/A"

    s = str(value).strip()

    return s if s else "N/A"


def format_entry(index: int, entry: dict) -> str:

    name = clean(entry.get("name"))

    father = clean(entry.get("father name"))

    address = clean(entry.get("address"))

    sim = clean(entry.get("circle/sim"))

    mobile = clean(entry.get("mobile"))

    alt_mobile = clean(entry.get("alternative mobile"))

    id_number = clean(entry.get("id number"))

    mail = clean(entry.get("mail"))

    return (
        f"\n━━━━━━━━━━━━━━━━━━\n"
        f"📌 RESULT #{index}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 Name: {name}\n"
        f"👨 Father: {father}\n"
        f"📱 Mobile: {mobile}\n"
        f"📞 Alt Mobile: {alt_mobile}\n"
        f"📡 SIM: {sim}\n"
        f"🏠 Address: {address}\n"
        f"🪪 ID: {id_number}\n"
        f"📧 Email: {mail}\n"
    )


def split_message(text: str, limit: int) -> list:

    lines = text.split("\n")

    chunks = []

    current = ""

    for line in lines:

        if len(current) + len(line) + 1 > limit:

            chunks.append(current)

            current = line + "\n"

        else:

            current += line + "\n"

    if current:
        chunks.append(current)

    return chunks


# ===================== MAIN =====================

def main():

    if not BOT_TOKEN:

        print("BOT_TOKEN not found.")

        return

    app = Application.builder().token(BOT_TOKEN).build()

    # User Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("num", num_command))
    app.add_handler(CommandHandler("help", help_command))

    # Admin
    app.add_handler(CommandHandler("stats", admin_stats))

    # Callback
    app.add_handler(
        CallbackQueryHandler(
            verify_callback,
            pattern="^verify_join$"
        )
    )

    logger.info("🤖 Bot Started Successfully")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
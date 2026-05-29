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

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)

# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv"8987520659:AAGWFLIGwK5ZV9DKZs8Maulq6Bc_w4zRKR0"

ADMIN_ID = 8351165824

# FULL API
API_URL = "https://aniketbramha.om-divine.workers.dev/?key=lundlo&num="

API_KEY = "lundlo"

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
                f"ðŸ“¢ {CHANNEL_1_NAME}",
                url=CHANNEL_1_LINK
            )
        ],
        [
            InlineKeyboardButton(
                f"ðŸ“¢ {CHANNEL_2_NAME}",
                url=CHANNEL_2_LINK
            )
        ],
        [
            InlineKeyboardButton(
                "âœ… VERIFY NOW",
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
                "ðŸš« YOU ARE BANNED FROM USING THIS BOT"
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
        "ðŸ”¥ PREMIUM ACCESS REQUIRED ðŸ”¥\n\n"
        "JOIN BOTH CHANNELS TO USE THIS BOT\n\n"
        f"ðŸ“¢ {CHANNEL_1_NAME}\n"
        f"ðŸ“¢ {CHANNEL_2_NAME}\n\n"
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
            "âœ… VERIFIED SUCCESSFULLY\n\n"
            "ðŸ” USE:\n"
            "/num 9876543210\n\n"
            "ðŸš€ PREMIUM ACCESS ENABLED"
        )

        await query.edit_message_text(text)

    else:

        await query.edit_message_text(
            "âŒ JOIN BOTH CHANNELS FIRST",
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
                f"ðŸ†• NEW USER\n\n"
                f"ðŸ‘¤ NAME: {user.first_name}\n"
                f"ðŸ†” ID: {user.id}\n"
                f"ðŸ“Š TOTAL USERS: {len(users)}"
            )

        except:
            pass

    text = (
        "ðŸ” *WELCOME TO PREMIUM NUMBER INFO BOT* ðŸ”\n\n"
        "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
        "âš¡ FAST & PREMIUM SEARCH\n"
        "ðŸ“¡ LIVE DATABASE ACCESS\n"
        "ðŸ”’ SECURE SYSTEM\n"
        "ðŸ‘¥ GROUP SUPPORTED\n"
        "ðŸš€ HIGH SPEED RESULTS\n"
        "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
        "ðŸ“² *AVAILABLE COMMANDS*\n\n"
        "ðŸ”¹ `/start` - Start Bot\n"
        "ðŸ”¹ `/help` - Help Menu\n"
        "ðŸ”¹ `/num <number>` - Search Number\n"
        "ðŸ”¹ `/stats` - Admin Stats\n"
        "ðŸ”¹ `/users` - All Users\n"
        "ðŸ”¹ `/bcast` - Broadcast Message\n"
        "ðŸ”¹ `/ban` - Ban User\n"
        "ðŸ”¹ `/unban` - Unban User\n\n"
        "ðŸ“Œ *EXAMPLE (Tap below to copy):*\n"
        "`/num `\n\n"
        "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
        "ðŸ”¥ *FEATURES*\n"
        "â€¢ Full Name\n"
        "â€¢ Father Name\n"
        "â€¢ Mobile Number\n"
        "â€¢ Alternative Number\n"
        "â€¢ Address Details\n"
        "â€¢ SIM / Circle Info\n"
        "â€¢ Email Information\n"
        "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
        "ðŸš€ *POWERED BY PLUS OFFICIAL*"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )

# =========================================================
# HELP
# =========================================================

async def help_command(update, context):

    text = (
        "ðŸ“š AVAILABLE COMMANDS\n\n"
        "/start - START BOT\n"
        "/help - HELP MENU\n"
        "/num <number> - SEARCH NUMBER\n\n"
        "ðŸ“² EXAMPLE:\n"
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
            "âŒ USE:\n/num 9876543210"
        )

        return

    number = context.args[0]

    if not number.isdigit():

        await update.message.reply_text(
            "âŒ INVALID NUMBER"
        )

        return

    log_search(user.id, number)

    msg = await update.message.reply_text(
        "ðŸ” SEARCHING PREMIUM DATABASE..."
    )

    try:

        url = f"{API_URL}/?key={API_KEY}&num={number}"

        async with httpx.AsyncClient(timeout=30) as client:

            response = await client.get(url)

            if response.status_code != 200:

                await msg.edit_text(
                    f"âŒ API ERROR\nSTATUS: {response.status_code}"
                )

                return

            raw_text = response.text.strip()

            print(raw_text)

            try:
                data = response.json()
            except:
                await msg.edit_text(
                    f"âŒ INVALID API RESPONSE\n\n{raw_text[:500]}"
                )
                return

    except Exception as e:

        await msg.edit_text(
            f"âŒ ERROR:\n{e}"
        )

        return

    text = (
        "ðŸ”¥ PREMIUM SEARCH RESULT ðŸ”¥\n\n"
        f"ðŸ“± NUMBER: {number}\n\n"
    )

    # ==========================================
    # DIRECT RESULT SHOW
    # ==========================================

    if isinstance(data, dict):

        for key, value in data.items():

            if isinstance(value, dict):

                text += (
                    "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
                    f"ðŸ“Œ RESULT\n\n"
                    f"ðŸ‘¤ NAME: {value.get('name', 'N/A')}\n"
                    f"ðŸ‘¨ FATHER: {value.get('father name', 'N/A')}\n"
                    f"ðŸ“± MOBILE: {value.get('mobile', 'N/A')}\n"
                    f"ðŸ“ž ALT: {value.get('alternative mobile', 'N/A')}\n"
                    f"ðŸ“¡ SIM: {value.get('circle/sim', 'N/A')}\n"
                    f"ðŸ  ADDRESS: {value.get('address', 'N/A')}\n"
                    f"ðŸªª ID: {value.get('id number', 'N/A')}\n"
                    f"ðŸ“§ EMAIL: {value.get('mail', 'N/A')}\n\n"
                )

        # IF API RETURNS NORMAL JSON
        if text.strip() == f"ðŸ”¥ PREMIUM SEARCH RESULT ðŸ”¥\n\nðŸ“± NUMBER: {number}":

            text += "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"

            for key, value in data.items():

                text += f"ðŸ”¹ {key} : {value}\n"

    else:

        text += "âŒ NO VALID DATA FOUND"

    if len(text) > 4000:
        text = text[:4000]

    # Added PLUS OFFICIAL button inline so it's clickable
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("ðŸš€ PLUS OFFICIAL", url=CHANNEL_2_LINK)]
    ])

    await msg.edit_text(text, reply_markup=reply_markup)

    # Auto Delete Timer (60 Seconds)
    async def delete_msg(message_obj):
        await asyncio.sleep(60)
        try:
            await message_obj.delete()
        except:
            pass
            
    asyncio.create_task(delete_msg(msg))

# =========================================================
# USERS
# =========================================================

async def users(update, context):

    if not is_admin(update.effective_user.id):
        return

    users_data = load_users()

    text = f"ðŸ‘¥ TOTAL USERS: {len(users_data)}\n\n"

    for uid, info in users_data.items():

        text += (
            f"ðŸ‘¤ {info['name']}\n"
            f"ðŸ†” {uid}\n"
            f"ðŸ”— @{info['username']}\n\n"
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

    try:
        # Multiline aur saare text ko theek se split karke lega
        message = update.message.text.split(None, 1)[1]
    except IndexError:
        await update.message.reply_text(
            "USE:\n/bcast MESSAGE"
        )
        return

    users_data = load_users()

    sent = 0
    failed = 0

    status = await update.message.reply_text(
        "ðŸ“¢ BROADCAST STARTED..."
    )

    for uid in users_data:

        try:

            await context.bot.send_message(
                chat_id=int(uid),
                text=f"ðŸ“¢ BROADCAST MESSAGE\n\n{message}"
            )

            sent += 1
            # Rate limit bachane ke liye chhota sa delay lagaya
            await asyncio.sleep(0.05)

        except:
            failed += 1

    await status.edit_text(
        f"âœ… BROADCAST COMPLETE\n\n"
        f"ðŸ“¨ SENT: {sent}\n"
        f"âŒ FAILED: {failed}"
    )

# =========================================================
# BAN USER
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
        f"ðŸš« USER BANNED:\n{uid}"
    )

# =========================================================
# UNBAN USER
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
        f"âœ… USER UNBANNED:\n{uid}"
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

    total_searches = sum(
        len(v) for v in history.values()
    )

    text = (
        "ðŸ“Š BOT STATISTICS\n\n"
        f"ðŸ‘¥ USERS: {len(users_data)}\n"
        f"ðŸš« BANNED: {len(banned)}\n"
        f"ðŸ” SEARCHES: {total_searches}"
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

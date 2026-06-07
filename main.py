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

# API URL
API_URL = "https://numapis.beastaccuserrr.workers.dev/?apikey=PAPAKIAPI&number="

# CHANNELS
CHANNEL_1_ID = "@cineinfo1"
CHANNEL_1_LINK = "https://t.me/cineinfo1"
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
        member = await bot.get_chat_member(channel, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📢 {CHANNEL_1_NAME}", url=CHANNEL_1_LINK)],
        [InlineKeyboardButton(f"📢 {CHANNEL_2_NAME}", url=CHANNEL_2_LINK)],
        [InlineKeyboardButton("✅ VERIFY NOW", callback_data="verify")]
    ])

async def check_join(update, context):
    user_id = update.effective_user.id
    if is_admin(user_id):
        return True
    if is_banned(user_id):
        await update.message.reply_text("🚫 YOU ARE BANNED FROM USING THIS BOT")
        return False

    bot = context.bot
    joined1 = await is_member(bot, user_id, CHANNEL_1_ID)
    joined2 = await is_member(bot, user_id, CHANNEL_2_ID)

    if joined1 and joined2:
        return True

    text = (
        "🔥 *PREMIUM ACCESS REQUIRED* 🔥\n\n"
        "JOIN BOTH CHANNELS TO USE THIS BOT\n\n"
        f"📢 {CHANNEL_1_NAME}\n"
        f"📢 {CHANNEL_2_NAME}\n\n"
        "AFTER JOIN CLICK VERIFY BUTTON"
    )
    await update.message.reply_text(text, reply_markup=join_keyboard())
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
        text = (
            "✅ VERIFIED SUCCESSFULLY\n\n"
            "🔍 USE:\n"
            "/num 9876543210\n\n"
            "🚀 PREMIUM ACCESS ENABLED"
        )
        await query.edit_message_text(text)
    else:
        await query.answer("❌ Please join both channels first!", show_alert=True)

# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        return
    user = update.effective_user
    register_user(user)

    text = (
        "🔥 *WELCOME TO PREMIUM NUMBER INFO BOT* 🔥\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ FAST & PREMIUM SEARCH\n"
        "📡 LIVE DATABASE ACCESS\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📲 *COMMAND*\n"
        "🔹 `/num 9876543210` - Search Number\n\n"
        "🚀 *POWERED BY PLUS OFFICIAL*"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔥 PLUS OFFICIAL 🔥", url=CHANNEL_2_LINK)]])
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

# =========================================================
# NUMBER SEARCH (FIXED FOR YOUR API RESPONSE)
# =========================================================

async def num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        return

    user = update.effective_user
    register_user(user)

    if not context.args:
        await update.message.reply_text("❌ USE LIKE THIS: `/num 9876543210`", parse_mode=ParseMode.MARKDOWN)
        return

    number = context.args[0]
    if not number.isdigit():
        await update.message.reply_text("❌ INVALID NUMBER")
        return

    log_search(user.id, number)
    msg = await update.message.reply_text("🔍 SEARCHING PREMIUM DATABASE...")

    try:
        url = f"{API_URL}{number}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            data = response.json()
    except Exception as e:
        await msg.edit_text(f"❌ ERROR: {e}")
        return

    # --- DATA PARSING LOGIC FOR YOUR API ---
    result_data = None
    if data.get("success") is True:
        results_list = data.get("result", {}).get("results", [])
        if results_list:
            result_data = results_list[0] # Pehla result uthao

    if not result_data:
        text = (
            "╔══════════════════════════╗\n"
            "        ❌ NO RESULT FOUND\n"
            "╚══════════════════════════╝\n\n"
            f"📱 SEARCHED NUMBER: {number}\n"
            "⚠️ Details not found in database."
        )
    else:
        # API Keys ke hisaab se data extract karna
        name = result_data.get("name", "N/A")
        father = result_data.get("father_name", "N/A")
        mobile = result_data.get("mobile", "N/A")
        alt = result_data.get("alternate_number", "N/A")
        circle = result_data.get("circle", "N/A")
        address = result_data.get("address", "N/A")
        id_num = result_data.get("id_number", "N/A") # Agar API mein ho
        email = result_data.get("email", "N/A")

        text = (
            "╔══════════════════════════╗\n"
            "       🔥 PREMIUM RESULT 🔥\n"
            "╚══════════════════════════╝\n\n"
            f"📱 *SEARCHED NUMBER*\n"
            f"➥ `{number}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 *FULL NAME*\n"
            f"➥ `{name}`\n\n"
            f"👨 *FATHER NAME*\n"
            f"➥ `{father}`\n\n"
            f"📞 *MOBILE NUMBER*\n"
            f"➥ `{mobile}`\n\n"
            f"☎️ *ALT NUMBER*\n"
            f"➥ `{alt}`\n\n"
            f"📡 *SIM / CIRCLE*\n"
            f"➥ `{circle}`\n\n"
            f"🏠 *ADDRESS*\n"
            f"➥ `{address}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚡ DATABASE STATUS : ACTIVE\n"
            "🔥 POWERED BY PLUS OFFICIAL 🔥"
        )

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔥 PLUS OFFICIAL 🔥", url=CHANNEL_2_LINK)]])
    result_message = await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
    
    # Auto delete result after 60 seconds
    asyncio.create_task(auto_delete_message(result_message, 60))

# =========================================================
# ADMIN COMMANDS
# =========================================================

async def stats(update, context):
    if not is_admin(update.effective_user.id): return
    users_count = len(load_users())
    await update.message.reply_text(f"📊 *STATS*\nTotal Users: {users_count}")

async def bcast(update, context):
    if not is_admin(update.effective_user.id) or not context.args: return
    msg_text = " ".join(context.args)
    users = load_users()
    for uid in users:
        try: await context.bot.send_message(uid, f"📢 *BROADCAST*\n\n{msg_text}", parse_mode=ParseMode.MARKDOWN)
        except: pass
    await update.message.reply_text("✅ Broadcast Sent")

# =========================================================
# MAIN
# =========================================================

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN NOT FOUND")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("num", num))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("bcast", bcast))
    app.add_handler(CallbackQueryHandler(verify, pattern="^verify$"))

    print("✅ BOT STARTED SUCCESSFULLY")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

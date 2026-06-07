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

# Security tip: Logging token is risky, but keeping it as per your original code
print("BOT TOKEN =>", BOT_TOKEN)

ADMIN_ID = 8351165824

# API - FIXED SYNTAX ERROR HERE
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
        "👋 *ACCESS DENIED!*\n\n"
        "You must join our channels to use this premium service.\n\n"
        "Please join below and click verify."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=join_keyboard())
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
            "✅ *VERIFIED SUCCESSFULLY*\n\n"
            "You can now search numbers using:\n"
            "`/num 9876543210`"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        await query.answer("❌ You haven't joined yet!", show_alert=True)

# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        return

    user = update.effective_user
    register_user(user)

    text = (
        f"🔥 *WELCOME {user.first_name} TO PREMIUM SEARCH* 🔥\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *Service:* Active\n"
        "📡 *Database:* Premium Live\n"
        "🚀 *Speed:* Ultra Fast\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📲 *Commands Available*\n"
        "🔹 `/num [number]` - Search Details\n"
        "🔹 `/help` - Support Menu\n\n"
        "📌 *Example:* `/num 9876543210`"
    )

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📢 OFFICIAL CHANNEL", url=CHANNEL_2_LINK)]])
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

# =========================================================
# HELP
# =========================================================

async def help_command(update, context):
    text = (
        "📚 *HELP MENU*\n\n"
        "1. Join both channels.\n"
        "2. Type `/num` followed by the mobile number.\n"
        "3. Results will be shown for 60 seconds.\n\n"
        "⚠️ *Note:* Don't use +91 or 0 before the number."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# =========================================================
# NUMBER SEARCH
# =========================================================

async def num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        return

    user = update.effective_user
    register_user(user)

    if not context.args:
        await update.message.reply_text("❌ *Error:* Please provide a number.\nUsage: `/num 9876543210`", parse_mode=ParseMode.MARKDOWN)
        return

    number = context.args[0]
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_text("❌ *Invalid Number Format!*")
        return

    log_search(user.id, number)
    msg = await update.message.reply_text("🔍 *Searching Premium Database...*", parse_mode=ParseMode.MARKDOWN)

    try:
        url = f"{API_URL}{number}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            if response.status_code != 200:
                await msg.edit_text(f"❌ API Error: {response.status_code}")
                return
            data = response.json()
    except Exception as e:
        await msg.edit_text(f"⚠️ *Connection Error:* {e}")
        return

    # Value Getter Helper
    def get_value(obj, keys):
        if not isinstance(obj, dict): return "N/A"
        for search_key in keys:
            for k, v in obj.items():
                if search_key.lower() == str(k).lower().strip():
                    return str(v).strip() if v else "N/A"
        return "N/A"

    # Finding Result Object
    result = None
    if isinstance(data, list) and len(data) > 0:
        result = data[0]
    elif isinstance(data, dict):
        if any(k in str(data.keys()).lower() for k in ["name", "mobile", "phone"]):
            result = data
        else:
            for v in data.values():
                if isinstance(v, dict):
                    result = v
                    break

    if not result:
        text = (
            "❌ *NO DETAILS FOUND*\n\n"
            f"📱 Number: `{number}`\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "This number is not available in our premium database."
        )
    else:
        name = get_value(result, ["name", "fullname", "full name"])
        father = get_value(result, ["father", "father name", "fname"])
        mobile = get_value(result, ["mobile", "phone", "number"])
        alt = get_value(result, ["alternative mobile", "alternate", "alt"])
        sim = get_value(result, ["circle", "sim", "operator"])
        address = get_value(result, ["address", "location"])
        idnum = get_value(result, ["id number", "id", "cnic"])
        email = get_value(result, ["email", "mail"])

        # Professional Layout
        text = (
            "💎 *PREMIUM SEARCH RESULT* 💎\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *NAME:* `{name}`\n"
            f"👨 *FATHER:* `{father}`\n"
            f"📞 *PHONE:* `{mobile}`\n"
            f"☎️ *ALT NUM:* `{alt}`\n"
            f"📡 *OPERATOR:* `{sim}`\n"
            f"🏠 *ADDRESS:* `{address}`\n"
            f"🪪 *ID/CNIC:* `{idnum}`\n"
            f"📧 *EMAIL:* `{email}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ *Status:* Success\n"
            "🚀 *Powered by @plus_official01*"
        )

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔥 PLUS OFFICIAL 🔥", url=CHANNEL_2_LINK)]])
    result_message = await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

    # Auto Delete to maintain privacy and keep chat clean
    asyncio.create_task(auto_delete_message(result_message, 60))

# =========================================================
# ADMIN COMMANDS
# =========================================================

async def users(update, context):
    if not is_admin(update.effective_user.id): return
    users_data = load_users()
    await update.message.reply_text(f"👥 *Total Users:* {len(users_data)}", parse_mode=ParseMode.MARKDOWN)

async def bcast(update, context):
    if not is_admin(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("Usage: `/bcast Hello everyone`")
        return
    message = " ".join(context.args)
    users_data = load_users()
    sent, failed = 0, 0
    status = await update.message.reply_text("📢 *Broadcast started...*")
    
    for uid in users_data.keys():
        try:
            await context.bot.send_message(int(uid), f"📢 *IMPORTANT UPDATE*\n\n{message}", parse_mode=ParseMode.MARKDOWN)
            sent += 1
        except:
            failed += 1
    await status.edit_text(f"✅ *Broadcast Complete*\n\n📨 Sent: {sent}\n❌ Failed: {failed}")

async def ban(update, context):
    if not is_admin(update.effective_user.id) or not context.args: return
    uid = context.args[0]
    banned = load_banned()
    if uid not in banned:
        banned.append(uid)
        save_banned(banned)
    await update.message.reply_text(f"🚫 User {uid} banned.")

async def unban(update, context):
    if not is_admin(update.effective_user.id) or not context.args: return
    uid = context.args[0]
    banned = load_banned()
    if uid in banned:
        banned.remove(uid)
        save_banned(banned)
    await update.message.reply_text(f"✅ User {uid} unbanned.")

async def stats(update, context):
    if not is_admin(update.effective_user.id): return
    users_data = load_users()
    history = load_history()
    total_searches = sum(len(v) for v in history.values())
    text = (
        "📊 *SYSTEM STATISTICS*\n\n"
        f"👥 Total Users: `{len(users_data)}`\n"
        f"🔍 Total Searches: `{total_searches}`\n"
        f"🚫 Banned Users: `{len(load_banned())}`"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# =========================================================
# MAIN
# =========================================================

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN NOT FOUND")
        return

    print("✅ BOT STARTED")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("num", num))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("bcast", bcast))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(verify, pattern="^verify$"))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

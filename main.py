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
ADMIN_ID = 8351165824

# API URL (Sahi format mein query parameter ke sath)
API_URL = "https://numapis.beastaccuserrr.workers.dev/?apikey=PAPAKIAPI&number="

# CHANNELS
CHANNEL_1_ID = "@cineinfo1"
CHANNEL_1_LINK = "https://t.me/cineinfo1"
CHANNEL_1_NAME = "📢 PLUS PRO"

CHANNEL_2_ID = "@plus_official01"
CHANNEL_2_LINK = "https://t.me/plus_official01"
CHANNEL_2_NAME = "📢 PLUS OFFICIAL"

# FILES
USERS_FILE = "users.json"
BANNED_FILE = "banned.json"
HISTORY_FILE = "history.json"
MAINTENANCE_FILE = "maintenance.json"

# LOGGING
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# INITIALIZE FILES
DEFAULT_FILES = {
    USERS_FILE: {}, 
    BANNED_FILE: [], 
    HISTORY_FILE: {},
    MAINTENANCE_FILE: {"status": False} # Default maintenance mode OFF rahega
}
for file, default in DEFAULT_FILES.items():
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default, f)

# =========================================================
# DATABASE HELPERS
# =========================================================
def load_json(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def load_users(): return load_json(USERS_FILE, {})
def save_users(data): save_json(USERS_FILE, data)
def load_banned(): return load_json(BANNED_FILE, [])
def save_banned(data): save_json(BANNED_FILE, data)
def load_history(): return load_json(HISTORY_FILE, {})
def save_history(data): save_json(HISTORY_FILE, data)

def is_admin(user_id): return int(user_id) == ADMIN_ID
def is_banned(user_id): return str(user_id) in [str(x) for x in load_banned()]

# Maintenance functions
def is_maintenance_on():
    data = load_json(MAINTENANCE_FILE, {"status": False})
    return data.get("status", False)

def set_maintenance(status: bool):
    save_json(MAINTENANCE_FILE, {"status": status})

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

async def auto_delete_message(message, delay=60):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass

# =========================================================
# FORCE JOIN LOGIC
# =========================================================
async def is_member(bot, user_id, channel):
    try:
        member = await bot.get_chat_member(channel, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

def join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{CHANNEL_1_NAME}", url=CHANNEL_1_LINK)],
        [InlineKeyboardButton(f"{CHANNEL_2_NAME}", url=CHANNEL_2_LINK)],
        [InlineKeyboardButton("🔄 VERIFY NOW", callback_data="verify")]
    ])

async def check_join(update, context):
    user_id = update.effective_user.id

    # Admin ke liye maintenance ya force join lagu nahi hota
    if is_admin(user_id):
        return True

    # 1. Maintenance Mode Check
    if is_maintenance_on():
        maintenance_text = (
            "🚧 *UNDER MAINTENANCE* 🚧\n\n"
            "Hello Dear User,\n"
            "Our servers are currently undergoing a scheduled upgrade to improve performance and add new premium databases. 🔥\n\n"
            "⏳ *Estimated Time:* We will be back online very soon!\n"
            "📢 *Stay Tuned:* Check out updates on our official channel.\n\n"
            "🙏 Thank you for your patience and support!"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Channel Updates", url=CHANNEL_2_LINK)]])
        await update.message.reply_text(maintenance_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        return False

    # 2. Ban Check
    if is_banned(user_id):
        await update.message.reply_text("⛔ *You are banned from using this bot.*", parse_mode=ParseMode.MARKDOWN)
        return False

    # 3. Channel Membership Check
    bot = context.bot
    joined1 = await is_member(bot, user_id, CHANNEL_1_ID)
    joined2 = await is_member(bot, user_id, CHANNEL_2_ID)

    if joined1 and joined2:
        return True

    text = (
        "⚠️ *🚨 ACCESS DENIED 🚨*\n\n"
        "To use this premium bot, you must join our official channels first!\n\n"
        "👉 *Please join the channels below and click Verify:* "
    )
    
    await update.message.reply_text(
        text,
        reply_markup=join_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    return False

# =========================================================
# CALLBACK VERIFY
# =========================================================
async def verify(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    bot = context.bot

    # Maintenance check inside callback
    if is_maintenance_on() and not is_admin(user_id):
        await query.answer("🚧 Bot is under maintenance! Please try later.", show_alert=True)
        return

    joined1 = await is_member(bot, user_id, CHANNEL_1_ID)
    joined2 = await is_member(bot, user_id, CHANNEL_2_ID)

    if joined1 and joined2:
        await query.answer("✅ Verification Successful!", show_alert=False)
        text = (
            "🎉 *VERIFIED SUCCESSFULLY!*\n\n"
            "Welcome to Premium Access. You can now search details.\n\n"
            "📌 *How to use:* \n"
            "👉 `/num 9876543210`"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        await query.answer("❌ You haven't joined both channels yet!", show_alert=True)

# =========================================================
# COMMANDS
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
                f"🆕 *NEW USER REGISTERED*\n\n"
                f"👤 Name: {user.first_name}\n"
                f"🆔 ID: `{user.id}`\n"
                f"📊 Total Users: {len(users)}",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            pass

    text = (
        "🔥 *WELCOME TO PREMIUM NUMBER INFO BOT* 🔥\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ Fast & Premium Search\n"
        "📡 Live Database Access\n"
        "🔒 Secure System\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📱 *AVAILABLE COMMANDS*\n"
        "🔹 `/start` - Start the bot\n"
        "🔹 `/num <number>` - Search Info\n"
        "🔹 `/help` - Help Menu\n\n"
        "⚡ *Powered by Plus Official*"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def help_command(update, context):
    if not await check_join(update, context): return
    await update.message.reply_text("📌 *Help Menu*\n\nUse `/num 9876543210` to get information about a phone number.", parse_mode=ParseMode.MARKDOWN)

async def num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        return

    user = update.effective_user
    register_user(user)

    if not context.args:
        await update.message.reply_text("❌ *Usage:* `/num 9876543210`", parse_mode=ParseMode.MARKDOWN)
        return

    number = context.args[0]
    if not number.isdigit():
        await update.message.reply_text("❌ *Invalid Number format.*", parse_mode=ParseMode.MARKDOWN)
        return

    log_search(user.id, number)
    msg = await update.message.reply_text("🔍 *Searching database... Please wait.*", parse_mode=ParseMode.MARKDOWN)

    try:
        url = f"{API_URL}{number}"
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.get(url)
            if response.status_code != 200:
                await msg.edit_text(f"❌ *API Error:* Status {response.status_code}", parse_mode=ParseMode.MARKDOWN)
                return
            data = response.json()
    except Exception as e:
        await msg.edit_text(f"❌ *Connection Error:* {e}", parse_mode=ParseMode.MARKDOWN)
        return

    def get_value(obj, keys):
        if not isinstance(obj, dict): return "N/A"
        for search_key in keys:
            for k, v in obj.items():
                if search_key.lower() == str(k).lower().strip():
                    return str(v).strip() if v else "N/A"
        return "N/A"

    result = data if isinstance(data, dict) else (data[0] if isinstance(data, list) and data else None)

    if not result:
        await msg.edit_text("❌ *No entry found for this number.*", parse_mode=ParseMode.MARKDOWN)
        return

    # Apke diye gae Custom Format ke mutabik variables extraction
    name_val = get_value(result, ['name', 'fullname', 'full name'])
    father_val = get_value(result, ['father', 'father name', 'fname'])
    phone_val = get_value(result, ['mobile', 'phone', 'number'])
    alt_val = get_value(result, ['alternative mobile', 'alternate mobile', 'alt'])
    operator_val = get_value(result, ['sim', 'circle', 'operator', 'circle/sim'])
    address_val = get_value(result, ['address', 'location'])
    id_val = get_value(result, ['id number', 'id', 'cnic'])
    email_val = get_value(result, ['email', 'mail'])

    # Strict government-issued ID filter (Aadhaar number privacy)
    if "aadhaar" in operator_val.lower() or "aadhaar" in address_val.lower() or "aadhaar" in name_val.lower():
        id_val = "[Redacted]"

    # Bilkul jaisa apne manga waisa layout
    text = (
        "💎 PREMIUM SEARCH RESULT 💎\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 NAME: {name_val}\n"
        f"👨 FATHER: {father_val}\n"
        f"📞 PHONE: {phone_val}\n"
        f"☎️ ALT NUM: {alt_val}\n"
        f"📡 OPERATOR: {operator_val}\n"
        f"🏠 ADDRESS: {address_val}\n"
        f"🪪 ID/CNIC: {id_val}\n"
        f"📧 EMAIL: {email_val}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ Status: Success\n"
        "🚀 Powered by @plus_official01"
    )
    
    # 60 seconds auto-delete functional inline markup layout ke sath
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔥 PLUS OFFICIAL 🔥", url=CHANNEL_2_LINK)]])
    res_msg = await msg.edit_text(text, reply_markup=keyboard)
    asyncio.create_task(auto_delete_message(res_msg, 60))

# =========================================================
# ADMIN CONTROLS
# =========================================================
async def maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if not context.args:
        current_status = "ON 🚧" if is_maintenance_on() else "OFF ✅"
        await update.message.reply_text(f"💡 *Current Maintenance Status:* `{current_status}`\n\nUse:\n`/maintenance on`\n`/maintenance off`", parse_mode=ParseMode.MARKDOWN)
        return
        
    action = context.args[0].lower()
    if action == "on":
        set_maintenance(True)
        await update.message.reply_text("🚧 *Maintenance Mode is now Enabled (ON).* Users will see the alert message.", parse_mode=ParseMode.MARKDOWN)
    elif action == "off":
        set_maintenance(False)
        await update.message.reply_text("✅ *Maintenance Mode is now Disabled (OFF).* Bot is fully accessible.", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("❌ Invalid argument. Use `on` or `off`.")

async def users(update, context):
    if is_admin(update.effective_user.id):
        await update.message.reply_text(f"👥 *Total Registered Users:* `{len(load_users())}`", parse_mode=ParseMode.MARKDOWN)

async def bcast(update, context):
    if not is_admin(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ *Usage:* `/bcast Your Message`", parse_mode=ParseMode.MARKDOWN)
        return
    
    message = " ".join(context.args)
    users_data = load_users()
    sent, failed = 0, 0
    status = await update.message.reply_text("📢 *Broadcast started...*")

    for uid in users_data.keys():
        try:
            await context.bot.send_message(int(uid), f"📢 *ANNOUNCEMENT*\n\n{message}", parse_mode=ParseMode.MARKDOWN)
            sent += 1
        except Exception:
            failed += 1
            
    await status.edit_text(f"✅ *Broadcast Finished.*\n\n📬 Sent: `{sent}`\n❌ Failed: `{failed}`", parse_mode=ParseMode.MARKDOWN)

async def ban(update, context):
    if not is_admin(update.effective_user.id) or not context.args: return
    uid = context.args[0]
    banned = load_banned()
    if uid not in banned:
        banned.append(uid)
        save_banned(banned)
    await update.message.reply_text(f"⛔ User `{uid}` has been banned.", parse_mode=ParseMode.MARKDOWN)

async def unban(update, context):
    if not is_admin(update.effective_user.id) or not context.args: return
    uid = context.args[0]
    banned = load_banned()
    if uid in banned:
        banned.remove(uid)
        save_banned(banned)
    await update.message.reply_text(f"✅ User `{uid}` unbanned.", parse_mode=ParseMode.MARKDOWN)

async def stats(update, context):
    if not is_admin(update.effective_user.id): return
    total_searches = sum(len(v) for v in load_history().values())
    await update.message.reply_text(f"📊 *BOT STATS*\n\n👥 Users: `{len(load_users())}`\n🔍 Total Searches: `{total_searches}`", parse_mode=ParseMode.MARKDOWN)

# =========================================================
# MAIN DRIVER
# =========================================================
def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN NOT FOUND")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # User Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("num", num))
    
    # Admin Commands
    app.add_handler(CommandHandler("maintenance", maintenance))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("bcast", bcast))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("stats", stats))
    
    # Callback Handlers
    app.add_handler(CallbackQueryHandler(verify, pattern="^verify$"))

    print("🚀 Bot Started Successfully.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

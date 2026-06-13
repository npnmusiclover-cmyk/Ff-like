import os
import json
import logging
import httpx
import asyncio
import re
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

# API URL
API_URL = "https://numinfo.eu.cc/api/check?apikey=starlegendapi&number="

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
    MAINTENANCE_FILE: {"status": False}
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

    if is_admin(user_id):
        return True

    if is_maintenance_on():
        maintenance_text = (
            "🚧 *UNDER MAINTENANCE* 🚧\n\n"
            "Hello Dear User,\n"
            "Our servers are currently undergoing a scheduled upgrade to improve performance.\n\n"
            "⏳ *Estimated Time:* We will be back online very soon!\n"
            "📢 *Stay Tuned:* Check out updates on our official channel.\n\n"
            "🙏 Thank you for your patience!"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Channel Updates", url=CHANNEL_2_LINK)]])
        await update.message.reply_text(maintenance_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        return False

    if is_banned(user_id):
        await update.message.reply_text("⛔ *You are banned from using this bot.*", parse_mode=ParseMode.MARKDOWN)
        return False

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
# WELCOME INTERFACE
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
        "⚡ *WELCOME TO PREMIUM NUMBER INFO BOT* ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Experience ultimate high-speed tracking system.\n"
        "Get instant access to live intelligence databases.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📱 *PUBLIC COMMANDS*\n"
        "• `/start` — Start or restart the bot interface\n"
        "• `/help` — Open the help and usage instructions\n"
        "• `/num <number>` — Search live database details\n\n"
    )
    
    if is_admin(user.id):
        text += (
            "⚙️ *ADMIN COMMANDS*\n"
            "• `/stats` — Check bot status & search traffic\n"
            "• `/users` — View total database registered users\n"
            "• `/bcast <msg>` — Send broadcast to all users\n"
            "• `/ban <id>` — Restrict a user from using the bot\n"
            "• `/unban <id>` — Unban a restricted user\n"
            "• `/maintenance <on/off>` — Toggle maintenance mode\n\n"
        )
        
    text += "✨ *Powered by PLUS OFFICIAL*"
    
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def help_command(update, context):
    if not await check_join(update, context): return
    await update.message.reply_text("📌 *Help Menu*\n\nUse `/num 9876543210` to get information about a phone number.", parse_mode=ParseMode.MARKDOWN)

# =========================================================
# ADVANCED NUMBER SEARCH PARSER (FIXED ERROR INTERCEPTOR)
# =========================================================
async def num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        return

    user = update.effective_user
    register_user(user)

    if not context.args:
        await update.message.reply_text("❌ *Usage LIKE THIS :* `/num 9876543210`", parse_mode=ParseMode.MARKDOWN)
        return

    number = context.args[0]
    if not number.isdigit():
        await update.message.reply_text("❌ *Invalid Number format.*", parse_mode=ParseMode.MARKDOWN)
        return

    log_search(user.id, number)
    msg = await update.message.reply_text("🔍 *Searching database... Please wait.*", parse_mode=ParseMode.MARKDOWN)

    # 1. PREMIUM & CLEAN CONNECTION ERROR TEXT
    try:
        url = f"{API_URL}{number}"
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url)
            raw_text = response.text
    except Exception:
        error_text = (
            "⚠️ *CONNECTION SLOW / SERVER LAG* ⚠️\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 *Status:* Request Timeout\n\n"
            "👉 Server response delayed hai ya aapka network slow hai.\n"
            "Kripya kuch der baad fir se koshish karein! ⏳\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🚀 *Powered by @plus_official01*"
        )
        await msg.edit_text(error_text, parse_mode=ParseMode.MARKDOWN)
        return

    # Phase 1: Try Standard JSON Parsing
    data = None
    try:
        data = response.json()
    except Exception:
        try:
            fixed_text = raw_text.strip()
            if not fixed_text.startswith("{"):
                fixed_text = "{" + fixed_text
            data = json.loads(fixed_text)
        except Exception:
            data = None

    # 2. INTERCEPT EXPLICIT ERROR OR "NO DATA FOUND" FROM API
    if "no data found" in raw_text.lower() or (data and str(data.get("status")).lower() == "error"):
        not_found_text = (
            "❌ *NUMBER DETAILS NOT FOUND* ❌\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔍 *Searched:* `{}`\n\n"
            "Afsos! Is number ka koi bhi data hamare premium database me nahi mila.\n"
            "Kripya ek baar number check karke dobara koshish karein. 👍\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🚀 *Powered by @plus_official01*"
        ).format(number)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔥 PLUS OFFICIAL 🔥", url=CHANNEL_2_LINK)]])
        await msg.edit_text(not_found_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        return

    name_val = father_val = phone_val = alt_val = operator_val = address_val = id_val = email_val = "N/A"

    # Phase 2: Extracting Values via JSON (If Data Found Successfully)
    if data and "0" in data:
        result = data["0"]
        def get_val(key):
            val = result.get(key, "N/A")
            if val is None or str(val).strip().lower() in ["null", "n/a", ""]:
                return "N/A"
            return str(val).strip()

        name_val = get_val("name")
        father_val = get_val("father name")
        phone_val = get_val("mobile")
        alt_val = get_val("alternative mobile")
        operator_val = get_val("circle/sim")
        address_val = get_val("address")
        id_val = get_val("id number")
        email_val = get_val("mail")

    # Phase 3: Extracting Values via Regex Fallback
    else:
        def extract_field(text, field_name):
            pattern = rf'"{field_name}"\s*:\s*(?:"([^"]*)"|([^,\s}}]+))'
            match = re.search(pattern, text)
            if match:
                val = match.group(1) if match.group(1) is not None else match.group(2)
                if val is None or val.strip().lower() in ["null", "n/a", ""]:
                    return "N/A"
                return val.strip()
            return "N/A"

        if "name" in raw_text or "mobile" in raw_text:
            name_val = extract_field(raw_text, "name")
            father_val = extract_field(raw_text, "father name")
            phone_val = extract_field(raw_text, "mobile")
            alt_val = extract_field(raw_text, "alternative mobile")
            operator_val = extract_field(raw_text, "circle/sim")
            address_val = extract_field(raw_text, "address")
            id_val = extract_field(raw_text, "id number")
            email_val = extract_field(raw_text, "mail")

    # 3. BACKUP INTERCEPTOR (Agar saare fields N/A reh jayein)
    if name_val == "N/A" and father_val == "N/A" and phone_val == "N/A":
        not_found_text = (
            "❌ *NUMBER DETAILS NOT FOUND* ❌\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔍 *Searched:* `{}`\n\n"
            "Afsos! Is number ka koi bhi data hamare premium database me nahi mila.\n"
            "Kripya ek baar number check karke dobara koshish karein. 👍\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🚀 *Powered by @plus_official01*"
        ).format(number)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔥 PLUS OFFICIAL 🔥", url=CHANNEL_2_LINK)]])
        await msg.edit_text(not_found_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        return

    # Security Filter Check
    if "aadhaar" in operator_val.lower() or "aadhaar" in address_val.lower() or "aadhaar" in name_val.lower():
        id_val = "[Redacted]"

    # Main Premium Success Template
    text = (
        "💎 *PREMIUM SEARCH RESULT* 💎\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *NAME:* `{name_val}`\n"
        f"👨 *FATHER:* `{father_val}`\n"
        f"📞 *PHONE:* `{phone_val}`\n"
        f"☎️ *ALT NUM:* `{alt_val}`\n"
        f"📡 *OPERATOR:* `{operator_val}`\n"
        f"🏠 *ADDRESS:* `{address_val}`\n"
        f"🪪 *ID/CNIC:* `{id_val}`\n"
        f"📧 *EMAIL:* `{email_val}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *Status:* Success\n"
        "🚀 *Powered by @plus_official01*"
    )
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔥 PLUS OFFICIAL 🔥", url=CHANNEL_2_LINK)]])
    res_msg = await msg.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
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
        await update.message.reply_text("🚧 *Maintenance Mode Enabled (ON).* ", parse_mode=ParseMode.MARKDOWN)
    elif action == "off":
        set_maintenance(False)
        await update.message.reply_text("✅ *Maintenance Mode Disabled (OFF).* ", parse_mode=ParseMode.MARKDOWN)

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
            
    await status.edit_text(f"📢 *Broadcast Finished.*\n\n📬 Sent: `{sent}`\n❌ Failed: `{failed}`", parse_mode=ParseMode.MARKDOWN)

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

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("num", num))
    app.add_handler(CommandHandler("maintenance", maintenance))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("bcast", bcast))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(verify, pattern="^verify$"))

    print("🚀 Bot Started Successfully.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

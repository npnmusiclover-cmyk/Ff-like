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

# New API URL
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
    if is_admin(user_id): return True

    if is_maintenance_on():
        maintenance_text = "🚧 *BOT UNDER MAINTENANCE* 🚧\n\nPlease wait for updates."
        await update.message.reply_text(maintenance_text, parse_mode=ParseMode.MARKDOWN)
        return False

    if is_banned(user_id):
        await update.message.reply_text("⛔ *You are banned.*")
        return False

    bot = context.bot
    joined1 = await is_member(bot, user_id, CHANNEL_1_ID)
    joined2 = await is_member(bot, user_id, CHANNEL_2_ID)

    if joined1 and joined2:
        return True

    text = "⚠️ *🚨 ACCESS DENIED 🚨*\n\nPlease join our channels to use the bot!"
    await update.message.reply_text(text, reply_markup=join_keyboard(), parse_mode=ParseMode.MARKDOWN)
    return False

# =========================================================
# COMMANDS & CALLBACKS
# =========================================================
async def verify(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    joined1 = await is_member(context.bot, user_id, CHANNEL_1_ID)
    joined2 = await is_member(context.bot, user_id, CHANNEL_2_ID)

    if joined1 and joined2:
        await query.answer("✅ Verified!", show_alert=False)
        await start(update, context) # Show welcome text after verify
    else:
        await query.answer("❌ Please join both channels!", show_alert=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Support for both Message and CallbackQuery
    user = update.effective_user
    msg_obj = update.message if update.message else update.callback_query.message

    if not await check_join(update, context):
        return

    register_user(user)

    # Naya Design Wala Welcome Text
    welcome_text = (
        "╭━━━〔 🔍 NUMBER INFO BOT 🔍 〕━━━╮\n\n"
        f"👋 *Welcome {user.first_name}*\n\n"
        "🎉 Aap Number Info Bot me safaltapoorvak join ho gaye hain.\n\n"
        "📱 Kisi bhi mobile number ki detail paane ke liye niche diya gaya command use kare:\n"
        "➜ `/num 9876543210` \n\n"
        "📋 Bot aapko number se judi available details kuch hi seconds me provide karega.\n\n"
        "⚡ *Fast Response* 🔒 *Easy to Use* 🤖 *24×7 Active*\n\n"
        "📌 *AVAILABLE COMMANDS:*\n"
        "🔹 `/start` - Restart the bot\n"
        "🔹 `/num <number>` - Get details\n"
        "🔹 `/help` - Support information\n\n"
    )

    if is_admin(user.id):
        welcome_text += (
            "⚙️ *ADMIN COMMANDS:*\n"
            "🔸 `/stats` - View stats\n"
            "🔸 `/users` - Total users\n"
            "🔸 `/bcast` - Broadcast message\n"
            "🔸 `/ban /unban` - User control\n"
            "🔸 `/maintenance <on/off>` - Toggle mode\n\n"
        )

    welcome_text += "╰━━━〔 ❤️ Thanks For Joining ❤️ 〕━━━╯"

    if update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def help_command(update, context):
    if not await check_join(update, context): return
    await update.message.reply_text("📌 *Help Menu*\n\nUse `/num 9876543210` to get information about a phone number.", parse_mode=ParseMode.MARKDOWN)

# =========================================================
# NUMBER SEARCH (UPDATED FOR NEW API FORMAT)
# =========================================================
async def num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        return

    user = update.effective_user
    if not context.args:
        await update.message.reply_text("❌ *Usage:* `/num 9876543210`", parse_mode=ParseMode.MARKDOWN)
        return

    number = context.args[0]
    if not (number.isdigit() and len(number) >= 10):
        await update.message.reply_text("❌ *Invalid Number format.*", parse_mode=ParseMode.MARKDOWN)
        return

    log_search(user.id, number)
    msg = await update.message.reply_text("🔍 *Searching database... Please wait.*", parse_mode=ParseMode.MARKDOWN)

    try:
        url = f"{API_URL}{number}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                await msg.edit_text(f"❌ *API Error:* Server responded with status {response.status_code}", parse_mode=ParseMode.MARKDOWN)
                return
            
            data = response.json()
    except Exception as e:
        await msg.edit_text(f"❌ *Connection Error:* {str(e)}", parse_mode=ParseMode.MARKDOWN)
        return

    # NEW PARSING LOGIC: API response me "0" key ke andar data hai
    if "0" not in data:
        await msg.edit_text("❌ *No information found for this number.*", parse_mode=ParseMode.MARKDOWN)
        return

    res = data["0"]

    def get_val(key):
        val = res.get(key, "N/A")
        return str(val).strip() if val and str(val).lower() != "null" else "N/A"

    # API Keys map (as per your JSON example)
    name = get_val("name")
    father = get_val("father name")
    address = get_val("address")
    sim = get_val("circle/sim")
    mobile = get_val("mobile")
    alt_mobile = get_val("alternative mobile")
    id_num = get_val("id number")
    email = get_val("mail")

    text = (
        "💎 *PREMIUM SEARCH RESULT* 💎\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *NAME:* `{name}`\n"
        f"👨 *FATHER:* `{father}`\n"
        f"📞 *PHONE:* `{mobile}`\n"
        f"☎️ *ALT NUM:* `{alt_mobile}`\n"
        f"📡 *OPERATOR:* `{sim}`\n"
        f"🏠 *ADDRESS:* `{address}`\n"
        f"🪪 *ID/CNIC:* `{id_num}`\n"
        f"📧 *EMAIL:* `{email}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *Status:* Success\n"
        "🚀 *Powered by PLUS OFFICIAL*"
    )
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔥 PLUS OFFICIAL 🔥", url=CHANNEL_2_LINK)]])
    res_msg = await msg.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    asyncio.create_task(auto_delete_message(res_msg, 120))

# =========================================================
# ADMIN CONTROLS (Stats, Broadcast, etc.)
# =========================================================
async def maintenance(update, context):
    if not is_admin(update.effective_user.id): return
    if not context.args: return
    action = context.args[0].lower()
    set_maintenance(True if action == "on" else False)
    await update.message.reply_text(f"🚧 Maintenance is now {'ON' if action == 'on' else 'OFF'}.")

async def users(update, context):
    if is_admin(update.effective_user.id):
        await update.message.reply_text(f"👥 *Total Users:* `{len(load_users())}`", parse_mode=ParseMode.MARKDOWN)

async def bcast(update, context):
    if not is_admin(update.effective_user.id) or not context.args: return
    msg = " ".join(context.args)
    all_users = load_users()
    sent = 0
    for uid in all_users.keys():
        try:
            await context.bot.send_message(int(uid), f"📢 *ANNOUNCEMENT*\n\n{msg}", parse_mode=ParseMode.MARKDOWN)
            sent += 1
            await asyncio.sleep(0.05)
        except: continue
    await update.message.reply_text(f"✅ Broadcast sent to {sent} users.")

async def ban(update, context):
    if not is_admin(update.effective_user.id) or not context.args: return
    uid = str(context.args[0])
    banned = load_banned()
    if uid not in banned: banned.append(uid); save_banned(banned)
    await update.message.reply_text(f"⛔ User {uid} banned.")

async def unban(update, context):
    if not is_admin(update.effective_user.id) or not context.args: return
    uid = str(context.args[0])
    banned = load_banned()
    if uid in banned: banned.remove(uid); save_banned(banned)
    await update.message.reply_text(f"✅ User {uid} unbanned.")

async def stats(update, context):
    if not is_admin(update.effective_user.id): return
    history = load_history()
    total_searches = sum(len(v) for v in history.values())
    await update.message.reply_text(f"📊 *STATS*\n\nUsers: {len(load_users())}\nSearches: {total_searches}", parse_mode=ParseMode.MARKDOWN)

# =========================================================
# MAIN
# =========================================================
def main():
    if not BOT_TOKEN: return
    app = Application.builder().token(BOT_TOKEN).build()

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

    print("🚀 Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

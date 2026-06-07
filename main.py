import os
import json
import logging
import httpx
import asyncio
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode, ChatType
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

# =========================================================
# ⚙️ CONFIGURATION
# =========================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 8351165824  # Aapki ID

# API ENDPOINTS
NUM_API = "https://numapis.beastaccuserrr.workers.dev/?apikey=PAPAKIAPI&number="
GST_API = "https://rohit-gst-api-q9p1.onrender.com/gst?number="
RC_API = "https://rc-info-1api.onrender.com/api/vehicle-info?rc="

# CHANNELS (Yahan se dono manage honge)
CHANNELS = [
    {"id": "@cineinfo1", "name": "⭐ PLUS PRO", "link": "https://t.me/cineinfo1"},
    {"id": "@plus_official01", "name": "🔥 PLUS OFFICIAL", "link": "https://t.me/plus_official01"}
]

# FILES
USERS_FILE = "users.json"
BANNED_FILE = "banned.json"
SETTINGS_FILE = "settings.json"

# =========================================================
# 🛠️ DATABASE HANDLERS
# =========================================================
def load_data(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f: json.dump(default, f)
    with open(file, "r") as f: return json.load(f)

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=2)

users_db = load_data(USERS_FILE, {})
banned_db = load_data(BANNED_FILE, [])
settings = load_data(SETTINGS_FILE, {"num": True, "gst": True, "rc": True})

# =========================================================
# 🛡️ SECURITY & FORCE JOIN
# =========================================================
async def is_member(bot, user_id):
    if user_id == ADMIN_ID: return True
    if str(user_id) in banned_db: return "BANNED"
    
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch["id"], user_id)
            if member.status in ["left", "kicked"]: return False
        except: return False
    return True

async def send_force_join(update, context):
    keyboard = [
        [InlineKeyboardButton(CHANNELS[0]["name"], url=CHANNELS[0]["link"])],
        [InlineKeyboardButton(CHANNELS[1]["name"], url=CHANNELS[1]["link"])],
        [InlineKeyboardButton("✅ VERIFY JOIN", callback_data="verify_join")]
    ]
    text = (
        "╔════════════════════════╗\n"
        "       🚫 ACCESS DENIED 🚫\n"
        "╚════════════════════════╝\n\n"
        "You must join our both channels to use this bot.\n\n"
        "1️⃣ Join @cineinfo1\n"
        "2️⃣ Join @plus_official01\n\n"
        "After joining, click the verify button below."
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# =========================================================
# 📞 SEARCH COMMANDS
# =========================================================

async def num_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    check = await is_member(context.bot, user_id)
    if check == "BANNED": return await update.message.reply_text("❌ You are banned from this bot.")
    if not check: return await send_force_join(update, context)
    
    if not settings["num"]: return await update.message.reply_text("⚠️ Num Search is under Maintenance.")
    if not context.args: return await update.message.reply_text("💡 Usage: `/num 9876543210`", parse_mode=ParseMode.MARKDOWN)

    num = context.args[0]
    m = await update.message.reply_text("🔍 `Searching Database...`", parse_mode=ParseMode.MARKDOWN)
    
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.get(f"{NUM_API}{num}")
            data = r.json()
        
        if data.get("success") and data["result"]["results"]:
            res = data["result"]["results"][0]
            text = (
                "💎 **PREMIUM SEARCH RESULT** 💎\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **NAME:** `{res.get('name', 'N/A')}`\n"
                f"👨 **FATHER:** `{res.get('father_name', 'N/A')}`\n"
                f"📞 **PHONE:** `{res.get('mobile', num)}`\n"
                f"☎️ **ALT NUM:** `{res.get('alternate_number', 'N/A')}`\n"
                f"📡 **OPERATOR:** `{res.get('circle', 'N/A')}`\n"
                f"🏠 **ADDRESS:** `{res.get('address', 'N/A')}`\n"
                f"🪪 **ID/CNIC:** `{res.get('id_number', 'N/A')}`\n"
                f"📧 **EMAIL:** `{res.get('email', 'N/A')}`\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "⚡ **Status:** Success\n"
                "🚀 **Powered by @plus_official01**"
            )
            await m.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        else: await m.edit_text("❌ **No Records Found.**")
    except: await m.edit_text("⚠️ **API Error.**")

# Similar optimization for GST and RC
async def gst_cmd(update, context):
    user_id = update.effective_user.id
    if not await is_member(context.bot, user_id): return await send_force_join(update, context)
    if not settings["gst"]: return await update.message.reply_text("⚠️ GST Search is under Maintenance.")
    if not context.args: return await update.message.reply_text("Usage: `/gst 19BOKPS7056D1ZI`")
    
    m = await update.message.reply_text("🏢 `Fetching Business Info...`")
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.get(f"{GST_API}{context.args[0].upper()}")
            data = r.json()
        if data.get("success"):
            biz = data["data"]["business_info"]
            text = f"💎 **PREMIUM GST INFO** 💎\n━━━━━━━━━━━━━━━━━━━━━━\n🏢 **TRADE:** `{biz.get('trade_name')}`\n⚖️ **LEGAL:** `{biz.get('legal_name')}`\n🟢 **STATUS:** `{biz.get('status')}`\n━━━━━━━━━━━━━━━━━━━━━━"
            await m.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        else: await m.edit_text("❌ GST Not Found.")
    except: await m.edit_text("⚠️ API Error.")

async def rc_cmd(update, context):
    user_id = update.effective_user.id
    if not await is_member(context.bot, user_id): return await send_force_join(update, context)
    if not settings["rc"]: return await update.message.reply_text("⚠️ RC Search is under Maintenance.")
    if not context.args: return await update.message.reply_text("Usage: `/rc MH12DE1433`")
    
    m = await update.message.reply_text("🚗 `Fetching Vehicle Info...`")
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.get(f"{RC_API}{context.args[0].upper()}")
            data = r.json()
        if data.get("status") == "success":
            basic = data["basic_info"]
            text = f"💎 **PREMIUM RC INFO** 💎\n━━━━━━━━━━━━━━━━━━━━━━\n👤 **OWNER:** `{basic.get('owner_name')}`\n🚘 **MODEL:** `{basic.get('model_name')}`\n🛡️ **INSURANCE:** `{data['insurance'].get('status')}`\n━━━━━━━━━━━━━━━━━━━━━━"
            await m.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        else: await m.edit_text("❌ Vehicle Not Found.")
    except: await m.edit_text("⚠️ API Error.")

# =========================================================
# 🛠️ ADMIN COMMANDS
# =========================================================

async def admin_stats(update, context):
    if update.effective_user.id != ADMIN_ID: return
    text = (
        "📊 **BOT STATISTICS**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 **Total Users:** `{len(users_db)}` \n"
        f"🚫 **Banned Users:** `{len(banned_db)}` \n\n"
        "**Service Status:**\n"
        f"Num: {'✅' if settings['num'] else '❌'} | "
        f"GST: {'✅' if settings['gst'] else '❌'} | "
        f"RC: {'✅' if settings['rc'] else '❌'}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def broadcast(update, context):
    if update.effective_user.id != ADMIN_ID or not update.message.reply_to_message:
        return await update.message.reply_text("Reply to a message with /broadcast")
    
    count = 0
    for uid in users_db:
        try:
            await context.bot.copy_message(chat_id=uid, from_chat_id=update.message.chat_id, message_id=update.message.reply_to_message.message_id)
            count += 1
            await asyncio.sleep(0.05)
        except: pass
    await update.message.reply_text(f"📢 Broadcast sent to {count} users.")

async def ban_user(update, context):
    if update.effective_user.id != ADMIN_ID or not context.args: return
    uid = context.args[0]
    if uid not in banned_db:
        banned_db.append(uid)
        save_data(BANNED_FILE, banned_db)
        await update.message.reply_text(f"🚫 User `{uid}` Banned.")

async def unban_user(update, context):
    if update.effective_user.id != ADMIN_ID or not context.args: return
    uid = context.args[0]
    if uid in banned_db:
        banned_db.remove(uid)
        save_data(BANNED_FILE, banned_db)
        await update.message.reply_text(f"✅ User `{uid}` Unbanned.")

# =========================================================
# 📂 SYSTEM HANDLERS
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    check = await is_member(context.bot, user.id)
    
    if check == "BANNED": return await update.message.reply_text("❌ You are Banned.")
    if not check: return await send_force_join(update, context)

    # Register User
    if str(user.id) not in users_db:
        users_db[str(user.id)] = {"name": user.first_name, "date": str(datetime.now().date())}
        save_data(USERS_FILE, users_db)

    welcome = (
        f"👋 **Hello {user.first_name}!**\n\n"
        "🛡️ **OSINT PREMIUM SEARCH BOT**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🚀 **Commands:**\n"
        "📞 `/num [number]` - Phone Details\n"
        "🏢 `/gst [gstin]` - GST Business Info\n"
        "🚗 `/rc [vehicle_no]` - RC/RTO Details\n"
        "👤 `/profile` - My Details\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💎 **Status:** `Active Member` ✅"
    )
    await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN)

async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if await is_member(context.bot, q.from_user.id):
        await q.answer("✅ Success! Access Activated.", show_alert=True)
        await q.message.delete()
        await start(update, context)
    else:
        await q.answer("❌ Join BOTH channels first!", show_alert=True)

# =========================================================
# 🏁 MAIN EXECUTION
# =========================================================
def main():
    if not BOT_TOKEN: return print("BOT_TOKEN Missing!")
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("num", num_cmd))
    app.add_handler(CommandHandler("gst", gst_cmd))
    app.add_handler(CommandHandler("rc", rc_cmd))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="verify_join"))
    
    print("🚀 PREMIUM BOT DEPLOYED")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

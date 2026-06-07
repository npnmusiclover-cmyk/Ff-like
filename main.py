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
# ⚙️ CONFIGURATION
# =========================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 8351165824 

# API ENDPOINTS
NUM_API = "https://numapis.beastaccuserrr.workers.dev/?apikey=PAPAKIAPI&number="
GST_API = "https://rohit-gst-api-q9p1.onrender.com/gst?number="
RC_API = "https://rc-info-1api.onrender.com/api/vehicle-info?rc="

CHANNELS = [
    {"id": "@cineinfo1", "name": "⭐ PLUS PRO", "link": "https://t.me/cineinfo1"},
    {"id": "@plus_official01", "name": "🔥 PLUS OFFICIAL", "link": "https://t.me/plus_official01"}
]

USERS_FILE = "users.json"
SETTINGS_FILE = "settings.json"

# =========================================================
# 🛠️ DATABASE & SETTINGS
# =========================================================
def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f: json.dump(default, f)
    with open(file, "r") as f: return json.load(f)

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=2)

# Initial Settings
default_settings = {"num": True, "gst": True, "rc": True}
settings = load_json(SETTINGS_FILE, default_settings)

# =========================================================
# 🛡️ ACCESS CONTROL
# =========================================================
async def is_member(bot, user_id):
    if user_id == ADMIN_ID: return True
    for ch in CHANNELS:
        try:
            m = await bot.get_chat_member(ch["id"], user_id)
            if m.status not in ["member", "administrator", "creator"]: return False
        except: return False
    return True

def get_join_kb():
    btns = [[InlineKeyboardButton(ch["name"], url=ch["link"])] for ch in CHANNELS]
    btns.append([InlineKeyboardButton("✅ VERIFY ACCESS", callback_data="verify")])
    return InlineKeyboardMarkup(btns)

async def check_service(update, service_key):
    if not settings.get(service_key, True):
        text = (
            "⚠️ **SERVICE MAINTENANCE** ⚠️\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Developer has temporarily disabled **{service_key.upper()} Search** for upgrades.\n\n"
            "📢 Please check @plus_official01 for updates."
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        return False
    return True

# =========================================================
# 📞 NUMBER SEARCH (CUSTOM FORMAT)
# =========================================================
async def num_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_service(update, "num"): return
    if not await is_member(context.bot, update.effective_user.id):
        return await update.message.reply_text("❌ Join channels to search!", reply_markup=get_join_kb())

    if not context.args:
        return await update.message.reply_text("💡 Usage: `/num 9876543210`", parse_mode=ParseMode.MARKDOWN)

    num = context.args[0]
    m = await update.message.reply_text("🔍 `Searching Premium Database...`", parse_mode=ParseMode.MARKDOWN)
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(f"{NUM_API}{num}")
            data = r.json()

        if data.get("success") and data.get("result", {}).get("results"):
            res = data["result"]["results"][0]
            result_text = (
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
                "⚡ **Status:** `Success`\n"
                "🚀 **Powered by @plus_official01**"
            )
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔥 PLUS OFFICIAL 🔥", url=CHANNELS[1]["link"])]])
            await m.edit_text(result_text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
        else:
            await m.edit_text("❌ **NO RECORD FOUND IN DATABASE**")
    except: await m.edit_text("⚠️ **API SERVER DOWN**")

# =========================================================
# 🏢 GST SEARCH
# =========================================================
async def gst_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_service(update, "gst"): return
    if not await is_member(context.bot, update.effective_user.id):
        return await update.message.reply_text("❌ Join channels first!", reply_markup=get_join_kb())

    if not context.args:
        return await update.message.reply_text("💡 Usage: `/gst 19BOKPS7056D1ZI`", parse_mode=ParseMode.MARKDOWN)

    gst_num = context.args[0].upper()
    m = await update.message.reply_text("📡 `Querying GST Records...`", parse_mode=ParseMode.MARKDOWN)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(f"{GST_API}{gst_num}")
            data = r.json()

        if data.get("success"):
            biz = data["data"]["business_info"]
            addr = data["data"]["address"]
            result_text = (
                "💎 **PREMIUM GST RESULT** 💎\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏢 **TRADE:** `{biz.get('trade_name', 'N/A')}`\n"
                f"⚖️ **LEGAL:** `{biz.get('legal_name', 'N/A')}`\n"
                f"🔢 **GSTIN:** `{data['data'].get('gst_number')}`\n"
                f"💳 **PAN:** `{data['data'].get('pan_number')}`\n"
                f"🟢 **STATUS:** `{biz.get('status', 'N/A')}`\n"
                f"📅 **REG DATE:** `{biz.get('registration_date', 'N/A')}`\n"
                f"🏠 **ADDRESS:** `{addr.get('st')}, {addr.get('loc')}, {addr.get('dst')}, {addr.get('stcd')} - {addr.get('pncd')}`\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "🚀 **Powered by @plus_official01**"
            )
            await m.edit_text(result_text, parse_mode=ParseMode.MARKDOWN)
        else:
            await m.edit_text("❌ **INVALID GST NUMBER**")
    except: await m.edit_text("⚠️ **SERVER ERROR**")

# =========================================================
# 🚗 RC SEARCH
# =========================================================
async def rc_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_service(update, "rc"): return
    if not await is_member(context.bot, update.effective_user.id):
        return await update.message.reply_text("❌ Join channels first!", reply_markup=get_join_kb())

    if not context.args:
        return await update.message.reply_text("💡 Usage: `/rc MH12DE1433`", parse_mode=ParseMode.MARKDOWN)

    rc_num = context.args[0].upper()
    m = await update.message.reply_text("🏎️ `Extracting RTO Details...`", parse_mode=ParseMode.MARKDOWN)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(f"{RC_API}{rc_num}")
            data = r.json()

        if data.get("status") == "success":
            basic = data["basic_info"]
            veh = data["vehicle_details"]
            result_text = (
                "💎 **PREMIUM RC RESULT** 💎\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **OWNER:** `{basic.get('owner_name')}`\n"
                f"👨 **FATHER:** `{basic.get('fathers_name')}`\n"
                f"🚘 **MODEL:** `{basic.get('model_name')}`\n"
                f"🔢 **REG NO:** `{data.get('registration_number')}`\n"
                f"⛽ **FUEL:** `{veh.get('fuel_type')}`\n"
                f"⏳ **AGE:** `{data['validity'].get('vehicle_age')}`\n"
                f"🛡️ **INSURANCE:** `{data['insurance'].get('status')}`\n"
                f"📍 **RTO:** `{data['ownership_details'].get('rto')}`\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "🚀 **Powered by @plus_official01**"
            )
            await m.edit_text(result_text, parse_mode=ParseMode.MARKDOWN)
        else:
            await m.edit_text("❌ **VEHICLE NOT FOUND**")
    except: await m.edit_text("⚠️ **RC API ERROR**")

# =========================================================
# 🛠️ ADMIN MAINTENANCE COMMAND
# =========================================================
async def maintain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        return await update.message.reply_text("Usage: `/maintain <num/gst/rc>`")
    
    service = context.args[0].lower()
    if service in settings:
        settings[service] = not settings[service]
        save_json(SETTINGS_FILE, settings)
        status = "✅ ACTIVE" if settings[service] else "❌ MAINTENANCE"
        await update.message.reply_text(f"Service **{service.upper()}** is now {status}", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("Invalid service. Use num, gst, or rc.")

# =========================================================
# 📂 SYSTEM HANDLERS
# =========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users = load_json(USERS_FILE, {})
    users[str(user.id)] = {"name": user.first_name, "username": user.username}
    save_json(USERS_FILE, users)
    
    if not await is_member(context.bot, user.id):
        return await update.message.reply_text("⚠️ **ACCESS DENIED**\nJoin our channels to activate.", reply_markup=get_join_kb())

    welcome = (
        f"👋 **Welcome, {user.first_name}!**\n\n"
        f"🛡️ **PREMIUM OSINT BOT v3.0**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 **Available Commands:**\n"
        f"📞 `/num [number]` - Search Mobile Details\n"
        f"🏢 `/gst [gstin]` - Search Business Details\n"
        f"🚗 `/rc [vehicle_no]` - Search Vehicle Details\n\n"
        f"📊 **My Status:** `Premium Member`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 **Powered by @plus_official01**"
    )
    await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN)

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if await is_member(context.bot, q.from_user.id):
        await q.answer("✅ Verified!", show_alert=True)
        await q.message.delete()
        await start(update, context)
    else:
        await q.answer("❌ Join all channels first!", show_alert=True)

# =========================================================
# 🏁 MAIN
# =========================================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("num", num_search))
    app.add_handler(CommandHandler("gst", gst_search))
    app.add_handler(CommandHandler("rc", rc_search))
    app.add_handler(CommandHandler("maintain", maintain))
    app.add_handler(CallbackQueryHandler(verify, pattern="^verify$"))
    
    print("🚀 BOT STARTED SUCCESSFULLY")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

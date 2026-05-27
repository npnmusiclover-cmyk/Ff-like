import logging
import json
import os
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# ===================== CONFIGURATION =====================
BOT_TOKEN    = "8661261432:AAEvxdh7IWtt3j6z765_OphNtZZTsFsyiCw"
API_KEY      = "https://paid.proportalx.workers.dev/leak?key=SupportMe&query="
API_URL      = "https://numinfo.eu.cc/api/check"

# Admin User ID
ADMIN_ID = 8351165824

# Force Join Channels
CHANNEL_1_ID       = "@plus_official01"
CHANNEL_1_LINK     = "https://t.me/plus_official01"
CHANNEL_1_NAME     = "PLUS PRO"

CHANNEL_2_ID       = "@inffo_01"
CHANNEL_2_LINK     = "https://t.me/inffo_01"
CHANNEL_2_NAME     = "INFFO_01"

# Data files
USERS_FILE     = "users.json"
PROTECTED_FILE = "protected.json"
BANNED_FILE    = "banned.json"
HISTORY_FILE   = "history.json"
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
    """Log a number search for a user."""
    history = load_history()
    uid = str(user_id)
    if uid not in history:
        history[uid] = []
    history[uid].append({
        "number": number,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    # Keep only last 20 searches per user
    history[uid] = history[uid][-20:]
    save_history(history)


def register_user(user) -> bool:
    """Register user. Returns True if new user."""
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
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False


def join_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"➕ Join {CHANNEL_1_NAME}", url=CHANNEL_1_LINK),
            InlineKeyboardButton(f"➕ Join {CHANNEL_2_NAME}", url=CHANNEL_2_LINK),
        ],
        [
            InlineKeyboardButton("✅ I've Joined — Verify Now", callback_data="verify_join"),
        ]
    ])


def result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"📢 {CHANNEL_1_NAME}", url=CHANNEL_1_LINK),
            InlineKeyboardButton(f"📢 {CHANNEL_2_NAME}", url=CHANNEL_2_LINK),
        ]
    ])


async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id

    # Check ban first
    if is_banned(user_id) and not is_admin(user_id):
        await update.message.reply_text(
            "🚫 *You have been banned from using this bot\\.*\n"
            "Contact admin if you think this is a mistake\\.",
            parse_mode="MarkdownV2",
        )
        return False

    # Admin exempt from force join
    if is_admin(user_id):
        return True

    bot = context.bot
    joined1 = await is_member(bot, user_id, CHANNEL_1_ID)
    joined2 = await is_member(bot, user_id, CHANNEL_2_ID)

    if joined1 and joined2:
        return True

    not_joined = []
    if not joined1:
        not_joined.append(CHANNEL_1_NAME)
    if not joined2:
        not_joined.append(CHANNEL_2_NAME)

    msg = (
        "❌ *Access Denied\\!*\n\n"
        "To use this bot, you must join both channels first:\n\n"
        f"📢 *{CHANNEL_1_NAME}*\n"
        f"📢 *{CHANNEL_2_NAME}*\n\n"
        f"⚠️ *Not Joined:* {', '.join(not_joined)}\n\n"
        "After joining, press the *Verify* button below ✅"
    )
    await update.message.reply_text(msg, parse_mode="MarkdownV2", reply_markup=join_keyboard())
    return False


async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    bot = context.bot

    joined1 = await is_member(bot, user_id, CHANNEL_1_ID)
    joined2 = await is_member(bot, user_id, CHANNEL_2_ID)

    if joined1 and joined2:
        await query.edit_message_text(
            "✅ *Verified\\! You can now use the bot\\.*\n\n"
            "📲 Type `/num <mobile_number>` to get started\\.",
            parse_mode="MarkdownV2",
        )
    else:
        not_joined = []
        if not joined1:
            not_joined.append(CHANNEL_1_NAME)
        if not joined2:
            not_joined.append(CHANNEL_2_NAME)

        await query.edit_message_text(
            "❌ *Still not joined\\!*\n\n"
            f"⚠️ *Pending channels:* {', '.join(not_joined)}\n\n"
            "Please join both channels and verify again ✅",
            parse_mode="MarkdownV2",
            reply_markup=join_keyboard(),
        )


# ===================== USER COMMANDS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return

    user = update.effective_user
    is_new = register_user(user)

    # Notify admin about new user
    if is_new:
        users = load_users()
        total = len(users)
        username_display = f"@{user.username}" if user.username else "No Username"
        notify_msg = (
            f"🆕 *New User Joined!*\n\n"
            f"👤 *Name:* {user.first_name}\n"
            f"🔗 *Username:* {username_display}\n"
            f"🆔 *User ID:* `{user.id}`\n"
            f"📊 *Total Users Now:* `{total}`\n"
            f"🕒 *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=notify_msg,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.warning(f"Admin notify failed: {e}")

    await update.message.reply_text(
        "🔍 *Welcome to Number Info Bot!*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📲 *How to use:*\n"
        "Type `/num <mobile_number>` to look up any number.\n\n"
        "📌 *Example:*\n"
        "`/num 9876543210`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ *What you get:*\n"
        "• Full Name & Father's Name\n"
        "• Address & ID Number\n"
        "• SIM / Circle Info\n"
        "• Alternative Mobile & Email\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Type /help to see all commands.\n\n"
        "⚡ *Powered by @lakhan_lakhnotra*",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """User: /help — show commands based on role"""
    if not await check_force_join(update, context):
        return

    user_id = update.effective_user.id

    # Admin gets full admin help
    if is_admin(user_id):
        await update.message.reply_text(
            "🛠️ *Admin Help Panel*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 *User Commands*\n"
            "`/start` — Start the bot\n"
            "`/num <number>` — Search a mobile number\n"
            "`/help` — Show this help message\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📊 *Overview*\n"
            "`/stats` — Full bot stats + user list\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "👥 *User Management*\n"
            "`/users` — List all registered users\n"
            "`/searchuser <query>` — Search by name/username\n"
            "`/deleteuser <id>` — Remove user from DB\n"
            "`/history <user_id>` — View user's search history\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🚫 *Ban Management*\n"
            "`/ban <user_id>` — Ban a user\n"
            "`/unban <user_id>` — Unban a user\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🔒 *Number Protection*\n"
            "`/protect <number>` — Protect a number\n"
            "`/unprotect <number>` — Remove protection\n"
            "`/protectedlist` — List all protected numbers\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📢 *Broadcast*\n"
            "`/bcast <message>` — Broadcast to all users\n",
            parse_mode="Markdown",
        )
    else:
        # Regular user help
        await update.message.reply_text(
            "📖 *Help — Available Commands*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 *Bot Commands:*\n\n"
            "🔹 `/start` — Start / Restart the bot\n\n"
            "🔹 `/num <mobile_number>`\n"
            "   Search info for any mobile number\n"
            "   Example: `/num 9876543210`\n\n"
            "🔹 `/help` — Show this help message\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ *What You Get:*\n"
            "• Full Name & Father's Name\n"
            "• Home Address\n"
            "• ID Number\n"
            "• SIM / Circle Info\n"
            "• Alternative Mobile Number\n"
            "• Email Address\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ *Powered by @lakhan_lakhnotra*",
            parse_mode="Markdown",
        )


async def num_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return

    user = update.effective_user
    register_user(user)

    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a number!\n\n"
            "Usage: `/num 9876543210`",
            parse_mode="Markdown",
        )
        return

    mobile_number = context.args[0].strip()

    if not mobile_number.isdigit():
        await update.message.reply_text("❌ Invalid input! Please enter digits only.")
        return

    if len(mobile_number) < 7 or len(mobile_number) > 15:
        await update.message.reply_text("❌ Invalid number length! Please enter a valid mobile number.")
        return

    # Protected number check
    protected = load_protected()
    if mobile_number in protected:
        await update.message.reply_text(
            "🔒 *This number is protected.*\n"
            "Its data is not available for search.",
            parse_mode="Markdown",
        )
        return

    # Log the search
    log_search(user.id, mobile_number)

    searching_msg = await update.message.reply_text(
        f"🔍 Searching `{mobile_number}` ...\n⏳ Please wait...", parse_mode="Markdown"
    )

    try:
        params = {"apikey": API_KEY, "number": mobile_number}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(API_URL, params=params)
            response.raise_for_status()
            data = response.json()

    except httpx.TimeoutException:
        await searching_msg.edit_text("⏱️ Request timed out! Please try again.")
        return
    except httpx.HTTPStatusError as e:
        await searching_msg.edit_text(f"❌ API Error: HTTP {e.response.status_code}")
        return
    except Exception as e:
        await searching_msg.edit_text(f"❌ Error: {str(e)}")
        return

    # Delete the "searching..." message
    try:
        await searching_msg.delete()
    except Exception:
        pass

    entries = [val for key, val in data.items() if key != "credit" and isinstance(val, dict)]

    if not entries:
        await update.message.reply_text(
            f"❌ *No data found for:* `{mobile_number}`\n\n"
            "This number may not be in our database.",
            parse_mode="Markdown"
        )
        return

    all_blocks = []
    header = (
        f"🔎 *Number:* `{mobile_number}`\n"
        f"📊 *Total Results: {len(entries)}*\n"
    )
    all_blocks.append(header)

    for i, entry in enumerate(entries, start=1):
        all_blocks.append(format_entry(i, entry))

    all_blocks.append("\n⚡ *Powered by @lakhan_lakhnotra*")

    full_message = "\n".join(all_blocks)

    if len(full_message) <= 4096:
        await update.message.reply_text(
            full_message,
            parse_mode="Markdown",
            reply_markup=result_keyboard(),
        )
    else:
        chunks = split_message(full_message, 4096)
        for idx, chunk in enumerate(chunks):
            kb = result_keyboard() if idx == len(chunks) - 1 else None
            await update.message.reply_text(chunk, parse_mode="Markdown", reply_markup=kb)


# ===================== ADMIN COMMANDS =====================

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin: /users — show all registered users"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ This command is for admin only.")
        return

    users = load_users()
    total = len(users)

    if total == 0:
        await update.message.reply_text("📭 No users registered yet.")
        return

    lines = [f"👥 *Registered Users — Total: {total}*\n"]
    for i, (uid, info) in enumerate(users.items(), start=1):
        uname = f"@{info['username']}" if info.get("username") and info["username"] != "N/A" else "No Username"
        fname = info.get('first_name', 'N/A')
        lines.append(f"{i}\\. {escape_md(uname)} \\| `{info['id']}` \\| {escape_md(fname)}")

    full_msg = "\n".join(lines)
    chunks = split_message(full_msg, 4096)
    for chunk in chunks:
        await update.message.reply_text(chunk, parse_mode="MarkdownV2")


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin: /stats — full overview"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ This command is for admin only.")
        return

    users = load_users()
    protected = load_protected()
    banned = load_banned()
    history = load_history()

    total_searches = sum(len(v) for v in history.values())
    banned_ids = [str(b) for b in banned]

    stats_msg = (
        f"📊 *Bot Statistics*\n\n"
        f"👥 *Total Users:* `{len(users)}`\n"
        f"🔒 *Protected Numbers:* `{len(protected)}`\n"
        f"🚫 *Banned Users:* `{len(banned)}`\n"
        f"🔍 *Total Searches Logged:* `{total_searches}`\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Registered Users:*\n"
    )

    if users:
        user_lines = []
        for i, (uid, info) in enumerate(users.items(), start=1):
            uname = f"@{info['username']}" if info.get("username") and info["username"] != "N/A" else "No Username"
            ban_tag = " 🚫" if str(uid) in banned_ids else ""
            fname = info.get('first_name', 'N/A')
            joined = info.get('joined', 'N/A')
            user_lines.append(
                f"\n{i}. {uname}{ban_tag}\n"
                f"    🆔 `{info['id']}` | {fname}\n"
                f"    📅 Joined: {joined}"
            )
        stats_msg += "".join(user_lines)
    else:
        stats_msg += "\nNo users yet."

    chunks = split_message(stats_msg, 4096)
    for chunk in chunks:
        await update.message.reply_text(chunk, parse_mode="Markdown")


async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin: /bcast <message> — broadcast to all users"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ This command is for admin only.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a message!\nUsage: `/bcast Your message here`",
            parse_mode="Markdown",
        )
        return

    broadcast_text = " ".join(context.args)
    users = load_users()
    total = len(users)

    if total == 0:
        await update.message.reply_text("📭 No users to broadcast to.")
        return

    status_msg = await update.message.reply_text(f"📤 Broadcasting to {total} users...")

    success = 0
    failed = 0

    for uid, info in users.items():
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text=f"📢 *Announcement*\n\n{broadcast_text}\n\n⚡ *@lakhan_lakhnotra*",
                parse_mode="Markdown",
            )
            success += 1
        except Exception as e:
            logger.warning(f"Broadcast failed for {uid}: {e}")
            failed += 1

    await status_msg.edit_text(
        f"✅ *Broadcast Complete!*\n\n"
        f"📨 *Sent:* {success}\n"
        f"❌ *Failed:* {failed}\n"
        f"📊 *Total:* {total}",
        parse_mode="Markdown",
    )


async def admin_protect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin: /protect <number>"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ This command is for admin only.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a number!\nUsage: `/protect 9876543210`",
            parse_mode="Markdown",
        )
        return

    number = context.args[0].strip()
    if not number.isdigit():
        await update.message.reply_text("❌ Invalid! Digits only.")
        return

    protected = load_protected()
    if number in protected:
        await update.message.reply_text(f"ℹ️ Number `{number}` is already protected.", parse_mode="Markdown")
        return

    protected.append(number)
    save_protected(protected)

    await update.message.reply_text(
        f"🔒 *Number Protected!*\n\n"
        f"📱 `{number}` will no longer appear in search results.\n"
        f"📊 Total protected: `{len(protected)}`",
        parse_mode="Markdown",
    )


async def admin_unprotect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin: /unprotect <number>"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ This command is for admin only.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a number!\nUsage: `/unprotect 9876543210`",
            parse_mode="Markdown",
        )
        return

    number = context.args[0].strip()
    if not number.isdigit():
        await update.message.reply_text("❌ Invalid! Digits only.")
        return

    protected = load_protected()
    if number not in protected:
        await update.message.reply_text(f"ℹ️ Number `{number}` is not in the protected list.", parse_mode="Markdown")
        return

    protected.remove(number)
    save_protected(protected)

    await update.message.reply_text(
        f"🔓 *Number Unprotected!*\n\n"
        f"📱 `{number}` can now be searched again.\n"
        f"📊 Total protected: `{len(protected)}`",
        parse_mode="Markdown",
    )


async def admin_protected_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin: /protectedlist"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ This command is for admin only.")
        return

    protected = load_protected()
    if not protected:
        await update.message.reply_text("📭 No protected numbers.")
        return

    lines = [f"🔒 *Protected Numbers — Total: {len(protected)}*\n"]
    for i, num in enumerate(protected, start=1):
        lines.append(f"{i}. `{num}`")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def admin_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin: /ban <user_id>"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ This command is for admin only.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a User ID!\nUsage: `/ban 123456789`",
            parse_mode="Markdown",
        )
        return

    uid = context.args[0].strip()
    if not uid.isdigit():
        await update.message.reply_text("❌ Invalid User ID.")
        return

    if int(uid) == ADMIN_ID:
        await update.message.reply_text("❌ You cannot ban yourself!")
        return

    banned = load_banned()
    if uid in [str(b) for b in banned]:
        await update.message.reply_text(f"ℹ️ User `{uid}` is already banned.", parse_mode="Markdown")
        return

    banned.append(uid)
    save_banned(banned)

    try:
        await context.bot.send_message(
            chat_id=int(uid),
            text="🚫 *You have been banned from using this bot.*",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    await update.message.reply_text(
        f"🚫 *User Banned!*\n\n"
        f"🆔 User `{uid}` has been banned.\n"
        f"📊 Total banned: `{len(banned)}`",
        parse_mode="Markdown",
    )


async def admin_unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin: /unban <user_id>"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ This command is for admin only.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a User ID!\nUsage: `/unban 123456789`",
            parse_mode="Markdown",
        )
        return

    uid = context.args[0].strip()
    banned = load_banned()

    if uid not in [str(b) for b in banned]:
        await update.message.reply_text(f"ℹ️ User `{uid}` is not banned.", parse_mode="Markdown")
        return

    banned = [b for b in banned if str(b) != uid]
    save_banned(banned)

    try:
        await context.bot.send_message(
            chat_id=int(uid),
            text="✅ *You have been unbanned! You can use the bot again.*",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    await update.message.reply_text(
        f"✅ *User Unbanned!*\n\n"
        f"🆔 User `{uid}` can now use the bot again.",
        parse_mode="Markdown",
    )


async def admin_delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin: /deleteuser <user_id>"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ This command is for admin only.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a User ID!\nUsage: `/deleteuser 123456789`",
            parse_mode="Markdown",
        )
        return

    uid = context.args[0].strip()
    users = load_users()

    if uid not in users:
        await update.message.reply_text(f"ℹ️ User `{uid}` not found in database.", parse_mode="Markdown")
        return

    deleted_info = users.pop(uid)
    save_users(users)

    uname = f"@{deleted_info.get('username')}" if deleted_info.get('username') and deleted_info['username'] != "N/A" else "No Username"
    await update.message.reply_text(
        f"🗑️ *User Deleted!*\n\n"
        f"👤 {uname} (`{uid}`) removed from database.\n"
        f"📊 Total users now: `{len(users)}`",
        parse_mode="Markdown",
    )


async def admin_search_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin: /searchuser <query>"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ This command is for admin only.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a search query!\nUsage: `/searchuser john`",
            parse_mode="Markdown",
        )
        return

    query = " ".join(context.args).lower().strip()
    users = load_users()
    results = []

    for uid, info in users.items():
        name = (info.get("first_name") or "").lower()
        uname = (info.get("username") or "").lower()
        if query in name or query in uname or query in uid:
            results.append((uid, info))

    if not results:
        await update.message.reply_text(f"🔍 No users found matching `{query}`.", parse_mode="Markdown")
        return

    lines = [f"🔍 *Search Results for* `{query}` *— {len(results)} found:*\n"]
    for i, (uid, info) in enumerate(results, start=1):
        uname = f"@{info['username']}" if info.get("username") and info["username"] != "N/A" else "No Username"
        lines.append(f"{i}. {uname} | `{info['id']}` | {info.get('first_name', 'N/A')}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def admin_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin: /history <user_id>"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ This command is for admin only.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a User ID!\nUsage: `/history 123456789`",
            parse_mode="Markdown",
        )
        return

    uid = context.args[0].strip()
    history = load_history()

    if uid not in history or not history[uid]:
        await update.message.reply_text(f"📭 No search history found for user `{uid}`.", parse_mode="Markdown")
        return

    records = history[uid]
    lines = [f"🕒 *Search History for* `{uid}` *— {len(records)} records:*\n"]
    for i, record in enumerate(reversed(records), start=1):
        lines.append(f"{i}. `{record['number']}` — {record['time']}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin: /adminhelp — show all admin commands"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ This command is for admin only.")
        return

    await update.message.reply_text(
        "🛠️ *Admin Commands*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Overview*\n"
        "`/stats` — Full bot stats + user list\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "👥 *User Management*\n"
        "`/users` — List all registered users\n"
        "`/searchuser <query>` — Search user by name/username\n"
        "`/deleteuser <id>` — Remove user from database\n"
        "`/history <user_id>` — View user's search history\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🚫 *Ban Management*\n"
        "`/ban <user_id>` — Ban a user\n"
        "`/unban <user_id>` — Unban a user\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔒 *Number Protection*\n"
        "`/protect <number>` — Protect a number\n"
        "`/unprotect <number>` — Remove protection\n"
        "`/protectedlist` — List all protected numbers\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📢 *Broadcast*\n"
        "`/bcast <message>` — Broadcast to all users\n",
        parse_mode="Markdown",
    )


# ===================== HELPERS =====================

def escape_md(text: str) -> str:
    """Escape special characters for MarkdownV2."""
    special_chars = r'\_*[]()~`>#+-=|{}.!'
    for ch in special_chars:
        text = text.replace(ch, f'\\{ch}')
    return text


def clean(value) -> str:
    if value is None:
        return "N/A"
    s = str(value).strip().replace("!", " ")
    while "  " in s:
        s = s.replace("  ", " ")
    return s.strip() or "N/A"


def format_entry(index: int, entry: dict) -> str:
    name       = clean(entry.get("name"))
    father     = clean(entry.get("father name"))
    address    = clean(entry.get("address"))
    sim        = clean(entry.get("circle/sim"))
    mobile     = clean(entry.get("mobile"))
    alt_mobile = clean(entry.get("alternative mobile"))
    id_number  = clean(entry.get("id number"))
    mail       = clean(entry.get("mail"))

    return (
        f"┌─────────────────────\n"
        f"│ 📌 *Result #{index}*\n"
        f"├─────────────────────\n"
        f"│ 👤 *Name:* `{name}`\n"
        f"│ 👨 *Father:* `{father}`\n"
        f"│ 📱 *Mobile:* `{mobile}`\n"
        f"│ 📞 *Alt Mobile:* `{alt_mobile}`\n"
        f"│ 📡 *SIM/Circle:* `{sim}`\n"
        f"│ 🏠 *Address:* `{address}`\n"
        f"│ 🪪 *ID Number:* `{id_number}`\n"
        f"│ 📧 *Email:* `{mail}`\n"
        f"└─────────────────────"
    )


def split_message(text: str, limit: int) -> list:
    lines = text.split("\n")
    chunks, current = [], ""
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

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    # User commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("num", num_command))
    app.add_handler(CommandHandler("help", help_command))

    # Admin commands
    app.add_handler(CommandHandler("users", admin_users))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("bcast", admin_broadcast))
    app.add_handler(CommandHandler("protect", admin_protect))
    app.add_handler(CommandHandler("unprotect", admin_unprotect))
    app.add_handler(CommandHandler("protectedlist", admin_protected_list))
    app.add_handler(CommandHandler("ban", admin_ban))
    app.add_handler(CommandHandler("unban", admin_unban))
    app.add_handler(CommandHandler("deleteuser", admin_delete_user))
    app.add_handler(CommandHandler("searchuser", admin_search_user))
    app.add_handler(CommandHandler("history", admin_history))
    app.add_handler(CommandHandler("adminhelp", admin_help))

    # Callback
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="^verify_join$"))

    logger.info("🤖 Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

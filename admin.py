from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import database as db
from config import DEVELOPER_ID, COPYRIGHT
def is_developer(user_id): return int(user_id) == int(DEVELOPER_ID)
def admin_panel_text():
    s = db.get_stats()
    return f"👑 لوحة المدير\n👥 {s['total_users']}\n🔍 {s['total_scans']}\n✅ {s['success_scans']}\n❌ {s['fail_scans']}"
def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 تحديث", callback_data="admin:stats")],
        [InlineKeyboardButton("👥 المستخدمون", callback_data="admin:users")],
        [InlineKeyboardButton("📢 إعلان", callback_data="admin:broadcast")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back:main")]])
def users_list_text(limit=50):
    users = db.get_all_users()
    if not users: return "لا مستخدمين."
    text = f"👥 المستخدمون ({len(users)})\n"
    for u in users[:limit]:
        n = u.get("first_name") or "—"
        text += f"• {n} — {u['user_id']}\n"
    return text

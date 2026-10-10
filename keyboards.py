from telegram import InlineKeyboardButton, InlineKeyboardMarkup
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 أدوات تحليل المواقع", callback_data="menu:web")],
        [InlineKeyboardButton("🌐 أدوات الشبكات", callback_data="menu:net")],
        [InlineKeyboardButton("🛡️ فحص الأمان", callback_data="menu:sec")],
        [InlineKeyboardButton("🔐 كلمات المرور", callback_data="menu:pwd")],
        [InlineKeyboardButton("📡 معلومات DNS", callback_data="menu:dns")],
        [InlineKeyboardButton("📊 تقارير الفحص", callback_data="menu:rep")],
        [InlineKeyboardButton("📚 تعلم الأمن السيبراني", callback_data="menu:learn")],
        [InlineKeyboardButton("ℹ️ معلومات البوت", callback_data="menu:about")]])
def web_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ التحقق من URL", callback_data="web:validate")],
        [InlineKeyboardButton("🌐 استخراج النطاق", callback_data="web:domain")],
        [InlineKeyboardButton("📡 فحص DNS", callback_data="web:dns")],
        [InlineKeyboardButton("📍 عنوان IP", callback_data="web:ip")],
        [InlineKeyboardButton("📊 استجابة الموقع", callback_data="web:response")],
        [InlineKeyboardButton("🔒 شهادة HTTPS", callback_data="web:ssl")],
        [InlineKeyboardButton("📄 تقرير كامل", callback_data="web:full")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back:main")]])
def net_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 تحليل IP", callback_data="net:ipinfo")],
        [InlineKeyboardButton("🌐 DNS Lookup", callback_data="net:dnslookup")],
        [InlineKeyboardButton("📡 فحص منفذ TCP", callback_data="net:tcpport")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back:main")]])
def sec_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 فحص رابط", callback_data="sec:urlcheck")],
        [InlineKeyboardButton("🔐 ترويسات الأمان", callback_data="sec:headers")],
        [InlineKeyboardButton("💡 ضد التصيد", callback_data="sec:phishing")],
        [InlineKeyboardButton("🛡️ حماية الحسابات", callback_data="sec:account")],
        [InlineKeyboardButton("🔑 2FA", callback_data="sec:2fa")],
        [InlineKeyboardButton("📱 أمان Android", callback_data="sec:android")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back:main")]])
def pwd_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 توليد كلمة مرور", callback_data="pwd:generate")],
        [InlineKeyboardButton("📊 تقييم قوة", callback_data="pwd:strength")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back:main")]])
def dns_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("A", callback_data="dns:A"), InlineKeyboardButton("MX", callback_data="dns:MX")],
        [InlineKeyboardButton("NS", callback_data="dns:NS"), InlineKeyboardButton("TXT", callback_data="dns:TXT")],
        [InlineKeyboardButton("CNAME", callback_data="dns:CNAME"), InlineKeyboardButton("ALL", callback_data="dns:ALL")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back:main")]])
def rep_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 تقاريري", callback_data="rep:list")],
        [InlineKeyboardButton("🗑 حذف الكل", callback_data="rep:clear")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back:main")]])
def learn_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 الشبكات", callback_data="learn:net")],
        [InlineKeyboardButton("🔐 التشفير", callback_data="learn:crypto")],
        [InlineKeyboardButton("🕵️ الهندسة الاجتماعية", callback_data="learn:social")],
        [InlineKeyboardButton("🛡️ الحماية", callback_data="learn:protect")],
        [InlineKeyboardButton("⚖️ الأخلاقيات", callback_data="learn:ethics")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back:main")]])
def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 تحديث", callback_data="admin:stats")],
        [InlineKeyboardButton("👥 المستخدمون", callback_data="admin:users")],
        [InlineKeyboardButton("📢 إعلان", callback_data="admin:broadcast")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back:main")]])
def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back:main")]])
def cancel_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]])

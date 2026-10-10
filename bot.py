import logging, time
from datetime import datetime, timezone
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes)
import config, database as db, keyboards as kb
import security_tools as st, report_manager as rm, admin as adm
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
log = logging.getLogger("anas_cyber")
_rate = {}
def rate_ok(uid):
    now = time.time(); last = _rate.get(uid, 0)
    if now - last < config.RATE_LIMIT_SECONDS: return False
    _rate[uid] = now; return True
def check_user(update):
    u = update.effective_user
    if u is None: return (False, None)
    if db.is_blocked(u.id) and not adm.is_developer(u.id): return (False, u)
    db.register_user(u.id, u.username or "", u.first_name or "")
    return (True, u)
async def cmd_start(update, ctx):
    ok, u = check_user(update)
    if not ok:
        if u: await update.message.reply_text("🚫 محظور.")
        return
    await update.message.reply_text(config.MSG_WELCOME, reply_markup=kb.main_menu(), parse_mode=ParseMode.HTML)
async def cmd_menu(update, ctx):
    check_user(update)
    await update.message.reply_text("🏠 القائمة", reply_markup=kb.main_menu(), parse_mode=ParseMode.HTML)
async def cmd_help(update, ctx):
    check_user(update); await update.message.reply_text(config.MSG_HELP, parse_mode=ParseMode.HTML)
async def cmd_about(update, ctx):
    check_user(update); await update.message.reply_text(config.MSG_ABOUT, parse_mode=ParseMode.HTML)
async def cmd_rules(update, ctx):
    check_user(update); await update.message.reply_text(config.MSG_RULES, parse_mode=ParseMode.HTML)
async def cmd_status(update, ctx):
    check_user(update); s = db.get_stats()
    await update.message.reply_text(f"🟢 يعمل\n📌 {config.VERSION}\n👥 {s['total_users']}\n🔍 {s['total_scans']}", parse_mode=ParseMode.HTML)
async def cmd_cancel(update, ctx):
    check_user(update); ctx.user_data.clear()
    await update.message.reply_text("✅ إلغاء.", reply_markup=kb.main_menu())
async def cmd_report(update, ctx):
    ok, u = check_user(update)
    if not ok: return
    reports = rm.get_user_reports(u.id)
    if not reports: await update.message.reply_text("📭 لا تقارير."); return
    text = f"📊 تقاريرك ({len(reports)})\n"
    for r in reports[:10]: text += f"📄 {r['name']}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)
async def cmd_admin(update, ctx):
    ok, u = check_user(update)
    if not ok: return
    if not adm.is_developer(u.id): await update.message.reply_text("🚫 للمدير فقط."); return
    await update.message.reply_text(adm.admin_panel_text(), reply_markup=adm.admin_keyboard(), parse_mode=ParseMode.HTML)
async def on_callback(update, ctx):
    q = update.callback_query; u = q.from_user
    if db.is_blocked(u.id) and not adm.is_developer(u.id): await q.answer("🚫", show_alert=True); return
    db.register_user(u.id, u.username or "", u.first_name or "")
    data = q.data or ""; await q.answer()
    if data == "back:main":
        await q.edit_message_text("🏠 القائمة", reply_markup=kb.main_menu(), parse_mode=ParseMode.HTML); return
    if data == "cancel":
        ctx.user_data.clear(); await q.edit_message_text("✅ إلغاء.", reply_markup=kb.main_menu()); return
    menus = {"menu:web": ("🔍 تحليل المواقع", kb.web_menu), "menu:net": ("🌐 الشبكات", kb.net_menu), "menu:sec": ("🛡️ الأمان", kb.sec_menu), "menu:pwd": ("🔐 كلمات المرور", kb.pwd_menu), "menu:dns": ("📡 DNS", kb.dns_menu), "menu:rep": ("📊 التقارير", kb.rep_menu), "menu:learn": ("📚 التعلم", kb.learn_menu)}
    if data in menus:
        text, kbfn = menus[data]
        await q.edit_message_text(text, reply_markup=kbfn(), parse_mode=ParseMode.HTML); return
    if data == "menu:about":
        await q.edit_message_text(config.MSG_ABOUT, reply_markup=kb.back_button(), parse_mode=ParseMode.HTML); return
    prompts = {"web:validate": ("web_validate", "✅ أرسل الرابط:"), "web:domain": ("web_domain", "🌐 أرسل الرابط:"), "web:dns": ("web_dns", "📡 أرسل النطاق:"), "web:ip": ("web_ip", "📍 أرسل النطاق:"), "web:response": ("web_response", "📊 أرسل الرابط:"), "web:ssl": ("web_ssl", "🔒 أرسل النطاق:"), "web:full": ("web_full", "📄 أرسل الرابط:"), "net:ipinfo": ("net_ip", "🔍 أرسل IP:"), "net:dnslookup": ("web_dns", "🌐 أرسل النطاق:"), "net:tcpport": ("net_port", "📡 host port"), "sec:urlcheck": ("sec_url", "🔍 أرسل الرابط:"), "sec:headers": ("sec_headers", "🔐 أرسل الرابط:"), "pwd:generate": ("pwd_gen", "🔐 أرسل الطول:"), "pwd:strength": ("pwd_check", "📊 أرسل كلمة المرور:")}
    if data in prompts:
        key, prompt = prompts[data]; ctx.user_data["await"] = key
        await q.edit_message_text(prompt, reply_markup=kb.cancel_button(), parse_mode=ParseMode.HTML); return
    if data.startswith("dns:"):
        rt = data.split(":", 1)[1]; ctx.user_data["await"] = f"dns_{rt}"
        await q.edit_message_text(f"📋 أرسل النطاق ({rt}):", reply_markup=kb.cancel_button(), parse_mode=ParseMode.HTML); return
    if data == "rep:list":
        reports = rm.get_user_reports(u.id)
        if not reports: await q.edit_message_text("📭 لا تقارير.", reply_markup=kb.back_button()); return
        text = f"📊 تقاريرك ({len(reports)})\n"
        for r in reports[:10]: text += f"📄 {r['name']}\n"
        await q.edit_message_text(text, reply_markup=kb.back_button(), parse_mode=ParseMode.HTML); return
    if data == "rep:clear":
        n = rm.delete_user_reports(u.id)
        await q.edit_message_text(f"🗑 حُذف {n}.", reply_markup=kb.back_button()); return
    if data.startswith("admin:"):
        if not adm.is_developer(u.id): await q.answer("🚫", show_alert=True); return
        sub = data.split(":", 1)[1]
        if sub == "stats":
            await q.edit_message_text(adm.admin_panel_text(), reply_markup=adm.admin_keyboard(), parse_mode=ParseMode.HTML); return
        if sub == "users":
            await q.edit_message_text(adm.users_list_text(), reply_markup=adm.admin_keyboard(), parse_mode=ParseMode.HTML); return
        if sub == "broadcast":
            ctx.user_data["admin_await"] = "broadcast"
            await q.edit_message_text("📢 أرسل النص:", reply_markup=kb.cancel_button(), parse_mode=ParseMode.HTML); return
    static = {"sec:phishing": "💡 نصائح ضد التصيد\n1. تحقق\n2. لا تضغط\n3. HTTPS", "sec:account": "🛡️ حماية الحسابات\n🔑 قوية\n🔐 2FA", "sec:2fa": "🔑 2FA\nGoogle Authenticator / Authy", "sec:android": "📱 أمان Android\n✅ F-Droid\n✅ قفل الشاشة", "learn:net": "🌐 الشبكات\nIP/DNS/HTTP/TCP", "learn:crypto": "🔐 التشفير\nAES/RSA/SHA", "learn:social": "🕵️ الهندسة الاجتماعية\nPhishing", "learn:protect": "🛡️ الحماية\nكلمات قوية/2FA", "learn:ethics": "⚖️ الأخلاقيات\nافحص المصرح به"}
    if data in static:
        await q.edit_message_text(static[data], reply_markup=kb.back_button(), parse_mode=ParseMode.HTML); return
    await q.edit_message_text("❓ غير معروف.", reply_markup=kb.main_menu())
async def on_text(update, ctx):
    u = update.effective_user
    if not u: return
    if db.is_blocked(u.id) and not adm.is_developer(u.id): return
    db.register_user(u.id, u.username or "", u.first_name or "")
    if not rate_ok(u.id): await update.message.reply_text("⏳ انتظر."); return
    text = (update.message.text or "").strip()
    if not text: return
    if ctx.user_data.get("admin_await") == "broadcast":
        if not adm.is_developer(u.id): return
        ctx.user_data.pop("admin_await", None)
        users = db.get_all_users(); sent = 0
        for usr in users:
            try:
                await ctx.bot.send_message(usr["user_id"], f"📢 إعلان\n\n{text}", parse_mode=ParseMode.HTML); sent += 1
            except Exception: pass
        await update.message.reply_text(f"✅ أُرسل لـ {sent}", reply_markup=kb.main_menu()); return
    wait = ctx.user_data.get("await")
    if not wait:
        await update.message.reply_text("🏠 استخدم القائمة:", reply_markup=kb.main_menu()); return
    ctx.user_data.pop("await", None)
    msg = update.message
    handlers = {
        "web_validate": st.validate_url, "web_domain": st.extract_domain, "web_response": st.check_response, "web_ssl": st.check_ssl,
        "sec_url": st.validate_url, "sec_headers": st.check_security_headers, "net_ip": st.analyze_ip}
    if wait in handlers:
        ok, m, _ = handlers[wait](text)
        await msg.reply_text(m, reply_markup=kb.back_button(), parse_mode=ParseMode.HTML)
        db.log_scan(u.id, wait, text, m, ok); return
    if wait == "web_dns":
        ok, m, res = st.dns_lookup(text, "A"); body = m
        if res: body += "\n" + "\n".join(f"<code>{r}</code>" for r in res)
        await msg.reply_text(body, reply_markup=kb.back_button(), parse_mode=ParseMode.HTML)
        db.log_scan(u.id, "dns", text, body, ok); return
    if wait == "web_ip":
        ok, m, ips = st.resolve_ip(text); body = m
        if ips: body += "\n" + "\n".join(f"<code>{i}</code>" for i in ips)
        await msg.reply_text(body, reply_markup=kb.back_button(), parse_mode=ParseMode.HTML)
        db.log_scan(u.id, "ip", text, body, ok); return
    if wait == "net_port":
        p = text.split()
        if len(p) != 2: await msg.reply_text("❌ host port", reply_markup=kb.back_button()); return
        ok, m, _ = st.check_tcp_port(p[0], p[1])
        await msg.reply_text(m, reply_markup=kb.back_button(), parse_mode=ParseMode.HTML)
        db.log_scan(u.id, "tcp", text, m, ok); return
    if wait == "pwd_gen":
        try: l = int(text)
        except ValueError: await msg.reply_text("❌ رقم.", reply_markup=kb.back_button()); return
        ok, m, _ = st.generate_password(l)
        await msg.reply_text(m, reply_markup=kb.back_button(), parse_mode=ParseMode.HTML)
        try: await msg.delete()
        except Exception: pass
        db.log_scan(u.id, "gen_pwd", f"len={l}", "gen", ok); return
    if wait == "pwd_check":
        ok, m, _ = st.check_password_strength(text)
        await msg.reply_text(m, reply_markup=kb.back_button(), parse_mode=ParseMode.HTML)
        try: await msg.delete()
        except Exception: pass
        db.log_scan(u.id, "check_pwd", "hidden", "checked", ok); return
    if wait == "web_full":
        status = await msg.reply_text("⏳ جاري...")
        ok_v, m_v, norm = st.validate_url(text)
        if not ok_v: await status.edit_text(m_v, reply_markup=kb.back_button()); return
        parts = [f"📄 <b>تقرير</b>\n🌐 <code>{norm}</code>"]
        _, _, ips = st.resolve_ip(text)
        if ips: parts.append("📍 " + ", ".join(ips))
        _, _, info = st.check_response(text)
        if info: parts.append(f"📊 {info['status']}")
        body = "\n".join(parts)
        await status.edit_text(body, reply_markup=kb.back_button(), parse_mode=ParseMode.HTML)
        ok, path, name = rm.create_report(u.id, "full", norm, body)
        if ok:
            try:
                with open(path, "rb") as f: await msg.reply_document(document=f, filename=name, caption="📄 تقريرك")
            except Exception: pass
        db.log_scan(u.id, "full", norm, body, True); return
    if wait.startswith("dns_"):
        rt = wait.split("_", 1)[1]
        if rt == "ALL":
            recs = st.all_dns_records(text)
            if not recs: await msg.reply_text("❌ لا سجلات.", reply_markup=kb.back_button()); return
            body = f"📡 {text}\n\n"
            for r, vals in recs.items():
                body += f"{r}:\n"
                for v in vals: body += f"  {v}\n"
            await msg.reply_text(body, reply_markup=kb.back_button(), parse_mode=ParseMode.HTML)
            db.log_scan(u.id, "dns_all", text, body, True); return
        ok, m, res = st.dns_lookup(text, rt); body = m
        if res: body += "\n" + "\n".join(f"<code>{r}</code>" for r in res)
        await msg.reply_text(body, reply_markup=kb.back_button(), parse_mode=ParseMode.HTML)
        db.log_scan(u.id, f"dns_{rt}", text, body, ok); return
    await msg.reply_text("❓ غير معروف.", reply_markup=kb.main_menu())
async def on_error(update, ctx): log.error(f"Error: {ctx.error}", exc_info=ctx.error)
def main():
    db.init_db()
    log.info(f"{config.PROJECT_NAME} v{config.VERSION}")
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("about", cmd_about))
    app.add_handler(CommandHandler("rules", cmd_rules))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("report", cmd_report))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_error_handler(on_error)
    log.info("🚀 البوت يعمل...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=False)
if __name__ == "__main__": main()

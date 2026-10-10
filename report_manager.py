import os, re, secrets
from datetime import datetime, timezone
from config import REPORTS_DIR, COPYRIGHT, VERSION, DEV_NAME
def _safe(name): return re.sub(r"[^A-Za-z0-9_\-\.]", "_", name)[:80]
def create_report(user_id, scan_type, target, content):
    try:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        tok = secrets.token_hex(4)
        fname = f"report_{user_id}_{ts}_{tok}_{_safe(str(target))}.txt"
        fpath = REPORTS_DIR / fname
        header = f"{DEV_NAME} — ANAS CYBER OS PRO v{VERSION}\n{COPYRIGHT}\n\nالنوع: {scan_type}\nالهدف: {target}\nالوقت: {datetime.now(timezone.utc).isoformat()}\nالعضو: {user_id}\n\n"
        fpath.write_text(header + str(content), encoding="utf-8")
        return (True, str(fpath), fname)
    except Exception as e: return (False, None, f"خطأ: {e}")
def get_user_reports(user_id):
    try:
        uid = str(user_id)
        files = sorted(REPORTS_DIR.glob(f"report_{uid}_*.txt"), reverse=True)
        return [{"path": str(f), "name": f.name, "size": f.stat().st_size} for f in files]
    except Exception: return []
def delete_user_reports(user_id):
    try:
        uid = str(user_id); count = 0
        for f in REPORTS_DIR.glob(f"report_{uid}_*.txt"):
            try: f.unlink(); count += 1
            except Exception: pass
        return count
    except Exception: return 0

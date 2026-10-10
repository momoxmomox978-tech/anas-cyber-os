import sqlite3, threading
from datetime import datetime, timezone
from config import DB_FILE
_lock = threading.Lock()
_conn = None
def _get_conn():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
        _conn.row_factory = sqlite3.Row
    return _conn
def init_db():
    with _lock:
        c = _get_conn()
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY,
            username TEXT, first_name TEXT, joined_at TEXT,
            last_seen TEXT, is_blocked INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, scan_type TEXT, target TEXT, result TEXT,
            success INTEGER, created_at TEXT);
        """)
        c.commit()
def _now(): return datetime.now(timezone.utc).isoformat()
def register_user(user_id, username, first_name):
    with _lock:
        c = _get_conn(); now = _now()
        cur = c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        if cur.fetchone():
            c.execute("UPDATE users SET username=?, first_name=?, last_seen=? WHERE user_id=?",
                      (username, first_name, now, user_id))
        else:
            c.execute("INSERT INTO users (user_id, username, first_name, joined_at, last_seen) VALUES (?,?,?,?,?)",
                      (user_id, username, first_name, now, now))
        c.commit()
def is_blocked(user_id):
    with _lock:
        c = _get_conn()
        row = c.execute("SELECT is_blocked FROM users WHERE user_id=?", (user_id,)).fetchone()
        return bool(row and row["is_blocked"])
def log_scan(user_id, scan_type, target, result, success):
    with _lock:
        c = _get_conn()
        c.execute("INSERT INTO scans (user_id, scan_type, target, result, success, created_at) VALUES (?,?,?,?,?,?)",
                  (user_id, scan_type, target[:500], result[:2000], 1 if success else 0, _now()))
        c.commit()
def get_stats():
    with _lock:
        c = _get_conn()
        tu = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        ts = c.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        ss = c.execute("SELECT COUNT(*) FROM scans WHERE success=1").fetchone()[0]
        bl = c.execute("SELECT COUNT(*) FROM users WHERE is_blocked=1").fetchone()[0]
        return {"total_users": tu, "total_scans": ts, "success_scans": ss, "fail_scans": ts-ss, "blocked_users": bl}
def get_all_users():
    with _lock:
        c = _get_conn()
        return [dict(r) for r in c.execute("SELECT user_id, username, first_name FROM users WHERE is_blocked=0").fetchall()]

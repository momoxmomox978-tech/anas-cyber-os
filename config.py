from pathlib import Path
BOT_TOKEN = "8267295606:AAH2FipkJIIXW6m2hPbKIQn9Lr3zlCZE38Y"
DEVELOPER_ID = 8849144518
PROJECT_NAME = "ANAS CYBER OS PRO"
VERSION = "4.0"
DEV_NAME = "أنس خشان"
COPYRIGHT = "© 2026 أنس خشان — جميع الحقوق محفوظة"
BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
DB_FILE = BASE_DIR / "anas_cyber.db"
LOG_FILE = BASE_DIR / "bot.log"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
HTTP_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (AnasCyberOS)"
MAX_URL_LEN = 300
MAX_INPUT_LEN = 200
RATE_LIMIT_SECONDS = 5
MSG_WELCOME = "ANAS CYBER OS PRO v" + VERSION
MSG_RULES = "قواعد الاستخدام: للتعلم والفحص المصرح به فقط"
MSG_ABOUT = PROJECT_NAME + " — " + DEV_NAME
MSG_HELP = "الأوامر: /start /menu /help /about /rules /status /report /cancel /admin"

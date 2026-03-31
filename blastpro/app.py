import os
import sys
import logging
import threading
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("BlastPro_Core")

from config import (
    SECRET_KEY, PERMANENT_SESSION_LIFETIME,
    SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SAMESITE,
    UPLOAD_FOLDER, MAX_CONTENT_LENGTH, BOT_POLLING_ENABLED, NOTIF_BOT_TOKEN
)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_for=1)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME
app.config['SESSION_COOKIE_SECURE'] = SESSION_COOKIE_SECURE
app.config['SESSION_COOKIE_HTTPONLY'] = SESSION_COOKIE_HTTPONLY
app.config['SESSION_COOKIE_SAMESITE'] = SESSION_COOKIE_SAMESITE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/uploads/proofs', exist_ok=True)

from routes.misc import misc_bp, register_app_hooks
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.broadcast import broadcast_bp
from routes.targets import targets_bp
from routes.schedule import schedule_bp
from routes.templates import templates_bp
from routes.crm import crm_bp
from routes.auto_reply import auto_reply_bp
from routes.connection import connection_bp
from routes.admin import admin_bp

app.register_blueprint(misc_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(broadcast_bp)
app.register_blueprint(targets_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(templates_bp)
app.register_blueprint(crm_bp)
app.register_blueprint(auto_reply_bp)
app.register_blueprint(connection_bp)
app.register_blueprint(admin_bp)

register_app_hooks(app)

@app.context_processor
def inject_globals():
    return {'now': datetime.utcnow()}


@app.template_filter('wib')
def to_wib(dt_string):
    if not dt_string:
        return '—'
    try:
        dt = datetime.fromisoformat(str(dt_string).replace('Z', '+00:00'))
        wib = dt + timedelta(hours=7)
        return wib.strftime('%d %b %Y, %H:%M WIB')
    except Exception:
        return str(dt_string)[:16]


@app.template_filter('wib_short')
def to_wib_short(dt_string):
    if not dt_string:
        return '—'
    try:
        dt = datetime.fromisoformat(str(dt_string).replace('Z', '+00:00'))
        wib = dt + timedelta(hours=7)
        return wib.strftime('%d %b %Y')
    except Exception:
        return str(dt_string)[:10]


@app.template_filter('rupiah')
def to_rupiah(value):
    try:
        return f"Rp {int(float(value)):,}".replace(',', '.')
    except Exception:
        return f"Rp {value}"

try:
    from demo_routes import demo_bp
    if demo_bp:
        app.register_blueprint(demo_bp)
        logger.info("✅ demo_routes Blueprint registered.")
except ImportError:
    logger.info("ℹ️ demo_routes.py tidak ada, dilewati.")

try:
    from bot import run_bot_process
except ImportError as e:
    logger.warning(f"⚠️ Modul bot.py tidak ditemukan atau error: {e}")
    run_bot_process = None


def init_system_check():
    from extensions import supabase
    from config import SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASS
    from utils.security import PasswordVault
    from services.helpers import generate_ref_code
    from datetime import datetime

    if not supabase:
        logger.warning("⚠️ [INIT CHECK] Supabase tidak terhubung. Lewati pembuatan admin.")
        return

    try:
        res = supabase.table('users').select("id").eq('email', SUPER_ADMIN_EMAIL).execute()
        if not res.data:
            hashed = PasswordVault.hash_password(SUPER_ADMIN_PASS)
            supabase.table('users').insert({
                "email": SUPER_ADMIN_EMAIL,
                "username": "SuperAdmin",
                "password": hashed,
                "is_admin": True,
                "is_verified": True,
                "referral_code": generate_ref_code(),
                "plan_tier": "Agency",
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            logger.info(f"✅ [INIT CHECK] Super Admin '{SUPER_ADMIN_EMAIL}' berhasil dibuat.")
        else:
            logger.info("✅ [INIT CHECK] Super Admin sudah ada.")
    except Exception as e:
        logger.error(f"❌ [INIT CHECK] Gagal buat admin: {e}")


_startup_done = False


def startup():
    global _startup_done
    if _startup_done:
        logger.info("ℹ️ [BOOT] Startup sudah dijalankan, skip.")
        return
    _startup_done = True

    from extensions import supabase
    from services.scheduler import SchedulerWorker
    from services.auto_reply_service import AutoReplyService
    from services.helpers import start_self_ping

    init_system_check()

    if supabase:
        SchedulerWorker.start()

    AutoReplyService.start()

    start_self_ping()

    if BOT_POLLING_ENABLED and NOTIF_BOT_TOKEN and run_bot_process:
        bot_thread = threading.Thread(target=run_bot_process, name="TelegramBot", daemon=True)
        bot_thread.start()
        logger.info("✅ [BOOT] Sinyal Start Bot Terkirim.")
    else:
        logger.info("ℹ️ Telegram polling bot nonaktif. Set ENABLE_BOT_POLLING=true untuk menyalakan.")


_startup_thread = threading.Thread(target=startup, name="AppStartup", daemon=True)
_startup_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000, use_reloader=False)

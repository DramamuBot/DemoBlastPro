import os
import logging
import pytz
from datetime import timedelta

logger = logging.getLogger("BlastPro_Core")

SECRET_KEY = os.getenv('SECRET_KEY') or os.getenv('SESSION_SECRET')
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY wajib diisi di environment variables!")

IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production'

SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://mragfujywnfzayejgxlx.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yYWdmdWp5d25memF5ZWpneGx4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4NDYwODYsImV4cCI6MjA4OTQyMjA4Nn0.XVav3N6yE-JuMFEwjoOIfBJ0d5XbItVqBwpIkH3cjqo"

MASTER_KEY = os.getenv('MASTER_KEY')

API_ID = int(os.getenv('API_ID') or '0')
API_HASH = os.getenv('API_HASH') or ''

APP_TIMEZONE_STR = os.getenv('APP_TIMEZONE', 'Asia/Jakarta')
try:
    APP_TZ = pytz.timezone(APP_TIMEZONE_STR)
except pytz.UnknownTimeZoneError:
    APP_TZ = pytz.timezone('Asia/Jakarta')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

PERMANENT_SESSION_LIFETIME = timedelta(days=7)
SESSION_COOKIE_SECURE = IS_PRODUCTION
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

SITE_URL = os.getenv('SITE_URL') or os.getenv('RENDER_EXTERNAL_URL')
NOTIF_BOT_TOKEN = os.getenv("NOTIF_BOT_TOKEN")
NOTIF_BOT_USERNAME = os.getenv('NOTIF_BOT_USERNAME', 'NamaBotLu_bot')

SUPER_ADMIN_EMAIL = os.getenv('SUPER_ADMIN', 'admin@baba.com')
SUPER_ADMIN_PASS = os.getenv('PASS_ADMIN', 'admin123')
if SUPER_ADMIN_PASS == 'admin123':
    logger.warning("⚠️ [SECURITY] PASS_ADMIN masih menggunakan password default 'admin123'! Segera ganti di environment variables.")

DEMO_USER_EMAIL = os.getenv('DEMO_USER', 'user@blastpro.id')
DEMO_USER_PASS = os.getenv('PASS_USER', 'User1234')

BOT_POLLING_ENABLED = os.getenv("ENABLE_BOT_POLLING", "false").lower() in {"1", "true", "yes", "on"}

CSRF_EXEMPT_PREFIXES = ('/api/', '/live-demo/', '/ping', '/import_crm_api', '/import_crm_csv', '/import_targets_csv', '/scan_groups_api', '/save_bulk_targets', '/start_broadcast')

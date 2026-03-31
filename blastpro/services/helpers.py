import asyncio
import logging
import string
import random
import time
import httpx
import threading
from datetime import datetime
from config import ALLOWED_EXTENSIONS, SITE_URL, NOTIF_BOT_TOKEN
from extensions import supabase

logger = logging.getLogger("BlastPro_Core")


def run_async(coroutine):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coroutine)
            return future.result()
    else:
        return asyncio.run(coroutine)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_notification(user_id, title, message, notif_type='info'):
    """Simpan notifikasi in-app ke database."""
    if not supabase:
        return
    try:
        supabase.table('notifications').insert({
            'user_id': str(user_id),
            'title': title,
            'message': message,
            'type': notif_type,
            'is_read': False
        }).execute()
    except Exception as e:
        logger.error(f"⚠️ Gagal simpan notif in-app: {e}")


def send_telegram_alert(user_id, message, show_report_btn=False):
    if not supabase:
        logger.warning(f"⚠️ Skip notif user {user_id}: Database Disconnected")
        return
    try:
        res = supabase.table('users').select("notification_chat_id").eq('id', user_id).execute()
        if not res.data or not res.data[0]['notification_chat_id']:
            return

        chat_id = res.data[0]['notification_chat_id']
        notif_token = NOTIF_BOT_TOKEN
        if not notif_token:
            return

        url = f"https://api.telegram.org/bot{notif_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        if show_report_btn:
            payload["reply_markup"] = {
                "inline_keyboard": [[
                    {
                        "text": "🔍 Lihat Detail & Error",
                        "callback_data": f"menu_reports_{user_id}"
                    }
                ]]
            }

        httpx.post(url, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"⚠️ Gagal kirim notif: {e}")


def generate_ref_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def get_max_accounts(plan_tier: str) -> int:
    tier = (plan_tier or 'STARTER').upper()
    if 'AGENCY' in tier:
        return 10
    elif 'PRO' in tier:
        return 3
    return 1


def start_self_ping():
    site_url = SITE_URL
    if not site_url:
        logger.warning("⚠️ SITE_URL belum diset. Fitur Self-Ping mungkin tidak efektif.")
        return

    if not site_url.startswith('http'):
        site_url = f'https://{site_url}'

    ping_endpoint = f"{site_url}/ping"
    logger.info(f"🚀 Anti-Sleep Worker Started! Target: {ping_endpoint}")

    def _worker():
        while True:
            try:
                time.sleep(840)
                with httpx.Client(timeout=10) as client:
                    resp = client.get(ping_endpoint)
                    if resp.status_code == 200:
                        logger.info(f"💓 [Heartbeat] Server is Alive | Time: {datetime.utcnow()}")
                    else:
                        logger.warning(f"⚠️ [Heartbeat] Ping returned status: {resp.status_code}")
            except Exception as e:
                logger.error(f"❌ [Heartbeat] Ping Failed: {e}")
                time.sleep(60)

    threading.Thread(target=_worker, daemon=True, name="PingWorker").start()

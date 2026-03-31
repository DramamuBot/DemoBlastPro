import time
import logging
import random
import pytz
from datetime import datetime
from extensions import supabase, decrypt_session
from config import API_ID, API_HASH
from telethon import TelegramClient
from telethon.sessions import StringSession

logger = logging.getLogger("BlastPro_Core")

# Cache ringan untuk menghindari query berulang ke Supabase per request
_user_cache: dict = {}
CACHE_TTL = 60  # detik


class UserEntity:
    def __init__(self, u_data, t_data):
        self.id = u_data['id']
        self.email = u_data['email']
        self.is_admin = u_data.get('is_admin', False)
        self.is_banned = u_data.get('is_banned', False)

        self.referral_code = u_data.get('referral_code', '-')
        self.wallet_balance = u_data.get('wallet_balance', 0)
        self.notification_chat_id = u_data.get('notification_chat_id')
        self.username = u_data.get('username', '')

        raw_created = u_data.get('created_at')
        try:
            self.created_at = datetime.fromisoformat(raw_created.replace('Z', '+00:00')) if raw_created else datetime.utcnow()
        except Exception:
            self.created_at = datetime.utcnow()

        self.plan_tier = u_data.get('plan_tier', 'Starter')

        raw_sub_end = u_data.get('subscription_end')
        self.days_remaining = 0
        self.subscription_status = 'Expired'
        self.sub_end_date = None

        if raw_sub_end:
            try:
                end_date = datetime.fromisoformat(raw_sub_end.replace('Z', '+00:00'))
                self.sub_end_date = end_date
                now = datetime.now(pytz.utc)
                delta = end_date - now
                if delta.days >= 0:
                    self.days_remaining = delta.days
                    self.subscription_status = 'Active'
                else:
                    self.days_remaining = 0
                    self.plan_tier = 'Starter'
            except Exception as e:
                logger.error(f"Date Parse Error: {e}")

        self.telegram_account = None
        if t_data:
            self.telegram_account = type('TeleInfo', (object,), {
                'phone_number': t_data.get('phone_number'),
                'is_active': t_data.get('is_active', False),
                'session_string': t_data.get('session_string')
            })()


def invalidate_user_cache(user_id):
    """Hapus cache user tertentu — panggil setelah update data user."""
    _user_cache.pop(str(user_id), None)


class LocalAdminEntity:
    """Entitas admin lokal ketika Supabase tidak tersedia."""
    def __init__(self):
        self.id = 'local-admin'
        self.email = 'admin@blastpro.id'
        self.is_admin = True
        self.is_banned = False
        self.referral_code = '-'
        self.wallet_balance = 0
        self.notification_chat_id = None
        self.username = 'Admin'
        self.created_at = datetime.utcnow()
        self.plan_tier = 'Admin'
        self.days_remaining = 9999
        self.subscription_status = 'Active'
        self.sub_end_date = None
        self.telegram_account = None


class LocalUserEntity:
    """Entitas user biasa lokal ketika Supabase tidak tersedia."""
    def __init__(self):
        from config import DEMO_USER_EMAIL
        self.id = 'local-user'
        self.email = DEMO_USER_EMAIL
        self.is_admin = False
        self.is_banned = False
        self.referral_code = 'USER2025'
        self.wallet_balance = 0
        self.notification_chat_id = None
        self.username = 'user'
        self.created_at = datetime.utcnow()
        self.plan_tier = 'UMKM Pro'
        self.days_remaining = 28
        self.subscription_status = 'Active'
        self.sub_end_date = None
        self.telegram_account = type('TeleInfo', (object,), {
            'phone_number': '+6281234567890',
            'is_active': True,
            'session_string': None
        })()


def get_user_data(user_id, use_cache: bool = True):
    if str(user_id) == 'local-admin':
        return LocalAdminEntity()

    if str(user_id) == 'local-user':
        return LocalUserEntity()

    if not supabase:
        return None

    cache_key = str(user_id)
    now = time.time()

    if use_cache and cache_key in _user_cache:
        cached_at, cached_user = _user_cache[cache_key]
        if now - cached_at < CACHE_TTL:
            return cached_user

    try:
        u_res = supabase.table('users').select("*").eq('id', user_id).execute()
        if not u_res.data:
            return None
        user_raw = u_res.data[0]

        t_res = supabase.table('telegram_accounts').select("*").eq('user_id', user_id)\
            .eq('is_active', True).limit(1).execute()
        tele_raw = t_res.data[0] if t_res.data else None

        user_entity = UserEntity(user_raw, tele_raw)

        if use_cache:
            _user_cache[cache_key] = (now, user_entity)

        return user_entity
    except Exception as e:
        logger.error(f"DAL Error (get_user_data): {e}")
        return None


async def get_active_client(user_id):
    """
    Ambil TelegramClient yang sudah terautentikasi.
    Jika ada beberapa akun aktif, pilih secara acak (round-robin sederhana)
    untuk menghindari beban di satu akun saja.
    """
    if not supabase:
        return None
    try:
        res = supabase.table('telegram_accounts').select("session_string, phone_number")\
            .eq('user_id', user_id).eq('is_active', True).execute()
        if not res.data:
            logger.warning(f"Client Init: Tidak ada sesi aktif untuk UserID {user_id}")
            return None

        # Pilih akun secara acak jika ada lebih dari satu
        account = random.choice(res.data)
        session_str = decrypt_session(account['session_string'])

        if not session_str:
            logger.warning(f"Client Init: Session string kosong untuk {account.get('phone_number')}")
            return None

        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await client.connect()

        if not await client.is_user_authorized():
            logger.warning(f"Client Init: Sesi EXPIRED untuk {account.get('phone_number')}")
            await client.disconnect()
            supabase.table('telegram_accounts').update({'is_active': False})\
                .eq('user_id', user_id)\
                .eq('phone_number', account['phone_number'])\
                .execute()
            return None

        return client
    except Exception as e:
        logger.error(f"Client Init Error untuk UserID {user_id}: {e}")
        return None


def get_dashboard_context(user_id_from_session):
    user = get_user_data(user_id_from_session)
    if not user:
        return None
    if user.is_banned:
        return None
    return user

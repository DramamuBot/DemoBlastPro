import asyncio
import logging
import threading
import random
import time
import pytz
from datetime import datetime
from config import API_ID, API_HASH
from extensions import supabase, decrypt_session
from models.auto_reply import AutoReplyManager
from telethon import TelegramClient, events
from telethon.sessions import StringSession

logger = logging.getLogger("BlastPro_Core")

SUPERVISOR_INTERVAL = 30
MAX_RECONNECT_ATTEMPTS = 3
RECONNECT_BASE_DELAY = 5


class AutoReplyService:
    _loop = None
    _clients = {}
    _reconnect_attempts = {}
    _last_error = {}

    @classmethod
    def start(cls):
        threading.Thread(target=cls._background_process, daemon=True, name="AutoReplySatpam").start()
        logger.info("👮‍♂️ [SATPAM] AutoReply Service BERHASIL DINYALAKAN!")

    @classmethod
    def _background_process(cls):
        cls._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls._loop)
        cls._loop.run_until_complete(cls._main_supervisor())

    @classmethod
    async def _main_supervisor(cls):
        logger.info("👀 [SATPAM] Mulai patroli hemat RAM...")
        while True:
            try:
                if supabase:
                    acc_res = supabase.table('telegram_accounts').select("*").eq('is_active', True).execute()
                    all_accounts = acc_res.data or []

                    settings_res = supabase.table('auto_reply_settings').select("target_phone, user_id").eq('is_active', True).execute()
                    allowed_combos = {
                        (s['user_id'], AutoReplyManager.normalize_phone(s['target_phone']))
                        for s in (settings_res.data or [])
                    }

                    active_keys = []

                    for acc in all_accounts:
                        phone = AutoReplyManager.normalize_phone(acc['phone_number'])
                        if (acc['user_id'], phone) in allowed_combos or (acc['user_id'], 'all') in allowed_combos:
                            key = f"{acc['user_id']}_{acc['phone_number']}"
                            active_keys.append(key)

                            if key in cls._clients:
                                client = cls._clients[key]
                                try:
                                    if not client.is_connected():
                                        logger.warning(f"🔄 [SATPAM] Koneksi terputus, reconnect: {key}")
                                        await cls._reconnect_client(acc, key)
                                except Exception:
                                    await cls._reconnect_client(acc, key)
                            else:
                                attempts = cls._reconnect_attempts.get(key, 0)
                                if attempts < MAX_RECONNECT_ATTEMPTS:
                                    await cls._start_client(acc, key)
                                elif attempts >= MAX_RECONNECT_ATTEMPTS:
                                    last_err_time = cls._last_error.get(key, 0)
                                    if time.time() - last_err_time > 300:
                                        cls._reconnect_attempts[key] = 0
                        else:
                            key = f"{acc['user_id']}_{acc['phone_number']}"
                            if key in cls._clients:
                                await cls._stop_client(key)

                    for existing_key in list(cls._clients.keys()):
                        if existing_key not in active_keys:
                            await cls._stop_client(existing_key)

            except Exception as e:
                logger.error(f"⚠️ [SATPAM] Supervisor Error: {e}")

            await asyncio.sleep(SUPERVISOR_INTERVAL)

    @classmethod
    async def _reconnect_client(cls, acc_data, key):
        # reset_attempts=False agar counter tidak dihapus — _start_client yang menangani retry logic
        await cls._stop_client(key, reset_attempts=False)
        await asyncio.sleep(RECONNECT_BASE_DELAY)
        await cls._start_client(acc_data, key)

    @classmethod
    async def _start_client(cls, acc_data, key):
        try:
            session_str = decrypt_session(acc_data.get('session_string', ''))
            if not session_str:
                logger.warning(f"⚠️ [SATPAM] Session string kosong untuk {key}")
                cls._reconnect_attempts[key] = MAX_RECONNECT_ATTEMPTS
                cls._last_error[key] = time.time()
                return

            client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            await client.connect()

            if not await client.is_user_authorized():
                logger.warning(f"❌ [SATPAM] Sesi Invalid/Expired: {key}")
                await client.disconnect()
                cls._reconnect_attempts[key] = cls._reconnect_attempts.get(key, 0) + 1
                cls._last_error[key] = time.time()
                return

            user_id = acc_data['user_id']
            my_phone = AutoReplyManager.normalize_phone(acc_data['phone_number'])

            @client.on(events.NewMessage(incoming=True))
            async def incoming_handler(event):
                try:
                    me_obj = await client.get_me()
                    if event.sender_id == me_obj.id or event.message.via_bot_id:
                        return
                    if event.is_group or event.is_channel:
                        return

                    sender_id = event.sender_id
                    chat_text = event.raw_text.lower().strip()

                    settings = AutoReplyManager.get_settings(user_id, my_phone)
                    if not settings or not settings.get('is_active'):
                        return

                    keywords = AutoReplyManager.get_keywords(user_id)
                    response_text = None

                    specific_rules = [r for r in keywords if AutoReplyManager.normalize_phone(r.get('target_phone')) == my_phone]
                    global_rules = [r for r in keywords if r.get('target_phone') == 'all']
                    all_rules = specific_rules + global_rules

                    for rule in all_rules:
                        trigger_words = [w.strip() for w in rule['keyword'].split(',') if w.strip()]
                        matched = any(word in chat_text for word in trigger_words)
                        if matched:
                            response_text = rule['response']
                            logger.info(f"✅ [SATPAM] {my_phone} menjawab trigger ke {sender_id}")
                            break

                    if not response_text and settings.get('welcome_message'):
                        cooldown_min = settings.get('cooldown_minutes', 60)
                        log_res = supabase.table('reply_logs').select("last_reply_at")\
                            .eq('user_id', user_id).eq('sender_id', sender_id).execute()

                        should_reply = True
                        if log_res.data:
                            last_time = datetime.fromisoformat(log_res.data[0]['last_reply_at'].replace('Z', '+00:00'))
                            diff_min = (datetime.now(pytz.utc) - last_time).total_seconds() / 60
                            if diff_min < cooldown_min:
                                should_reply = False

                        if should_reply:
                            response_text = settings.get('welcome_message')
                            logger.info(f"👋 [SATPAM] {my_phone} kirim Welcome Message ke {sender_id}")

                    if response_text:
                        try:
                            input_chat = await event.get_input_chat()
                            async with client.action(input_chat, 'typing'):
                                await asyncio.sleep(random.uniform(1.5, 3.0))
                        except Exception:
                            pass
                        await event.reply(response_text)

                        log_data = {
                            'user_id': user_id,
                            'sender_id': sender_id,
                            'last_reply_at': datetime.utcnow().isoformat()
                        }
                        supabase.table('reply_logs').upsert(log_data, on_conflict="user_id, sender_id").execute()

                except Exception as handler_e:
                    logger.error(f"Handler Error {my_phone}: {handler_e}")

            cls._clients[key] = client
            cls._reconnect_attempts[key] = 0
            cls._last_error.pop(key, None)
            logger.info(f"👂 [SATPAM] Aktif Mendengarkan: {my_phone}")

        except Exception as e:
            logger.error(f"Gagal start client {key}: {e}")
            cls._reconnect_attempts[key] = cls._reconnect_attempts.get(key, 0) + 1
            cls._last_error[key] = time.time()

    @classmethod
    async def _stop_client(cls, key, reset_attempts: bool = True):
        client = cls._clients.pop(key, None)
        if client:
            try:
                await client.disconnect()
            except Exception as e:
                logger.warning(f"Error saat disconnect {key}: {e}")
            logger.info(f"💤 [SATPAM] Stop Listening: {key}")
        if reset_attempts:
            cls._reconnect_attempts.pop(key, None)
            cls._last_error.pop(key, None)

import asyncio
import logging
import threading
import random
import time
from datetime import datetime, timedelta
from config import APP_TZ, API_ID, API_HASH
from extensions import supabase, decrypt_session
from telethon import TelegramClient
from telethon.sessions import StringSession

logger = logging.getLogger("BlastPro_Core")


class SchedulerWorker:
    last_run_minute = None
    _exec_guard_lock = threading.Lock()
    _executed_run_keys = {}

    @staticmethod
    def start():
        threading.Thread(target=SchedulerWorker._loop, daemon=True, name="SchedulerEngine").start()
        logger.info("🕒 Scheduler Engine Started (Timezone: Asia/Jakarta)")

    @staticmethod
    def _loop():
        while True:
            try:
                tz_indo = APP_TZ
                now_indo = datetime.now(tz_indo)
                if SchedulerWorker.last_run_minute != now_indo.minute:
                    if supabase:
                        SchedulerWorker._process_schedules(now_indo)
                    SchedulerWorker.last_run_minute = now_indo.minute
                sleep_time = 60 - datetime.now().second
                if sleep_time < 0:
                    sleep_time = 1
                time.sleep(sleep_time)
            except Exception as e:
                logger.error(f"Scheduler Loop Error: {e}")
                time.sleep(60)

    @staticmethod
    def _process_schedules(current_time_indo):
        from services.helpers import send_telegram_alert
        try:
            future_time = current_time_indo + timedelta(minutes=5)
            upcoming = supabase.table('blast_schedules').select("user_id")\
                .eq('is_active', True)\
                .eq('run_hour', future_time.hour)\
                .eq('run_minute', future_time.minute)\
                .execute().data

            for job in upcoming:
                msg = (
                    "⏳ **PENGINGAT JADWAL**\n\n"
                    f"Jadwal Blast akan berjalan dalam **5 menit lagi** "
                    f"(Pukul {future_time.hour}:{future_time.minute:02d} WIB).\n\n"
                    "Pastikan akun Telegram pengirim (Sender) Anda aktif/online agar proses lancar."
                )
                threading.Thread(target=send_telegram_alert, args=(job['user_id'], msg)).start()

            current_hour = current_time_indo.hour
            current_minute = current_time_indo.minute
            res = supabase.table('blast_schedules').select("*")\
                .eq('is_active', True)\
                .eq('run_hour', current_hour)\
                .eq('run_minute', current_minute)\
                .execute()

            schedules = res.data
            if not schedules:
                return

            logger.info(f"🚀 EXECUTE: Ditemukan {len(schedules)} jadwal induk.")
            for task in schedules:
                threading.Thread(target=SchedulerWorker._execute_task, args=(task,)).start()

        except Exception as e:
            logger.error(f"Scheduler Process Error: {e}")

    @staticmethod
    def _execute_task(task):
        from services.helpers import send_telegram_alert, save_notification
        from models.template import MessageTemplateManager

        user_id = task['user_id']
        schedule_id = task.get('id')
        template_id = task.get('template_id')
        target_group_id = task.get('target_group_id')
        target_template_name = task.get('target_template_name')
        sender_phone = task.get('sender_phone')

        tz_indo = APP_TZ
        run_key = f"{schedule_id}:{datetime.now(tz_indo).strftime('%Y%m%d%H%M')}"
        with SchedulerWorker._exec_guard_lock:
            now_ts = time.time()
            SchedulerWorker._executed_run_keys = {
                k: v for k, v in SchedulerWorker._executed_run_keys.items() if (now_ts - v) < 7200
            }
            if run_key in SchedulerWorker._executed_run_keys:
                logger.warning(f"⏭️ Skip duplicate task execution: {run_key}")
                return
            SchedulerWorker._executed_run_keys[run_key] = now_ts

        message_content = "Halo! Ini pesan terjadwal otomatis."
        source_media = None

        if template_id:
            tmpl = MessageTemplateManager.get_template_by_id(template_id)
            if tmpl:
                message_content = tmpl['message_text']
                if tmpl.get('source_chat_id') and tmpl.get('source_message_id'):
                    source_media = {'chat': int(tmpl['source_chat_id']), 'id': int(tmpl['source_message_id'])}
            else:
                logger.error(f"Task Batal: Template ID {template_id} tidak ditemukan untuk User {user_id}")
                try:
                    supabase.table('blast_schedules').update({'is_active': False}).eq('id', schedule_id).execute()
                    logger.warning(f"Jadwal {schedule_id} dinonaktifkan otomatis karena template tidak ditemukan.")
                except Exception as deact_err:
                    logger.error(f"Gagal nonaktifkan jadwal {schedule_id}: {deact_err}")
                send_telegram_alert(user_id, "❌ **Jadwal Dinonaktifkan!**\nTemplate Pesan tidak valid atau sudah dihapus. Jadwal telah dimatikan otomatis. Harap edit jadwal dan pilih Template yang benar.")
                save_notification(user_id, 'Jadwal Dinonaktifkan', 'Template pesan tidak valid atau sudah dihapus. Jadwal dimatikan otomatis. Silakan edit jadwal.', 'error')
                return

        async def _async_send():
            client = None
            conn_error = None
            is_specific_sender = (sender_phone and sender_phone != 'auto')

            try:
                if is_specific_sender:
                    res = supabase.table('telegram_accounts').select("session_string")\
                        .eq('user_id', user_id).eq('phone_number', sender_phone).eq('is_active', True).execute()
                    if res.data:
                        client = TelegramClient(StringSession(decrypt_session(res.data[0]['session_string'])), API_ID, API_HASH, sequential_updates=True)
                        await client.connect()
                    else:
                        conn_error = f"⛔ Akun {sender_phone} mati/logout. Task dibatalkan demi keamanan branding."
                else:
                    res_auto = supabase.table('telegram_accounts').select("session_string, phone_number")\
                        .eq('user_id', user_id).eq('is_active', True).execute()
                    if res_auto.data:
                        client = TelegramClient(StringSession(decrypt_session(res_auto.data[0]['session_string'])), API_ID, API_HASH, sequential_updates=True)
                        await client.connect()
                    else:
                        conn_error = "Tidak ada akun Telegram yang aktif sama sekali."

                if not client or not await client.is_user_authorized():
                    supabase.table('blast_logs').insert({
                        "user_id": user_id, "group_name": "SYSTEM", "group_id": 0,
                        "status": "FAILED", "error_message": conn_error or "Auth Failed",
                        "created_at": datetime.utcnow().isoformat()
                    }).execute()
                    send_telegram_alert(user_id, f"❌ **Jadwal Gagal!**\n{conn_error}")
                    save_notification(user_id, 'Jadwal Gagal', conn_error or 'Akun Telegram tidak dapat terhubung.', 'error')
                    if client:
                        await client.disconnect()
                    return

            except Exception as e:
                logger.error(f"Scheduler Connect Error: {e}")
                return

            try:
                send_telegram_alert(user_id, f"🚀 **Jadwal Dimulai!**\nPengirim: {sender_phone if is_specific_sender else 'Auto'}")
                save_notification(user_id, 'Jadwal Blast Dimulai', f'Pengirim: {sender_phone if is_specific_sender else "Auto (rotasi)"}. Proses sedang berjalan...', 'info')

                src_msg_obj = None
                if source_media:
                    try:
                        src_msg_obj = await client.get_messages(source_media['chat'], ids=source_media['id'])
                    except Exception as e:
                        logger.warning(f"Gagal narik pesan asli: {e}")

                targets_query = supabase.table('blast_targets').select("*").eq('user_id', user_id)
                if target_template_name:
                    targets_query = targets_query.eq('template_name', target_template_name)
                elif target_group_id:
                    targets_query = targets_query.eq('id', target_group_id)

                raw_targets = targets_query.execute().data

                if not raw_targets:
                    send_telegram_alert(user_id, "⚠️ Target grup kosong.")
                    return

                send_queue = []
                for tg in raw_targets:
                    topic_ids = []
                    if tg.get('topic_ids'):
                        try:
                            topic_ids = [int(x.strip()) for x in str(tg['topic_ids']).split(',') if x.strip().isdigit()]
                        except Exception:
                            pass
                    destinations = topic_ids if topic_ids else [None]
                    for top_id in destinations:
                        send_queue.append({
                            'group_id': int(tg['group_id']),
                            'topic_id': top_id,
                            'group_name': tg.get('group_name', 'Unknown')
                        })

                async def process_queue(queue_list, attempt_phase):
                    next_retry_queue = []
                    success_count = 0
                    processed_since_break = 0
                    break_after = random.randint(20, 25)

                    for idx, item in enumerate(queue_list):
                        if processed_since_break >= break_after:
                            rest_seconds = random.randint(120, 300)
                            await asyncio.sleep(rest_seconds)
                            processed_since_break = 0
                            break_after = random.randint(20, 25)

                        try:
                            entity = await client.get_entity(item['group_id'])
                            await client.send_read_acknowledge(entity)
                            try:
                                async with client.action(entity, 'typing'):
                                    await asyncio.sleep(random.uniform(2, 5))
                            except Exception:
                                pass

                            if src_msg_obj:
                                await client.send_message(entity, src_msg_obj, reply_to=item['topic_id'])
                            else:
                                final_msg = message_content.replace("{name}", item['group_name'])
                                await client.send_message(entity, final_msg, reply_to=item['topic_id'])

                            supabase.table('blast_logs').insert({
                                "user_id": user_id, "group_name": item['group_name'], "group_id": str(item['group_id']),
                                "status": "SUCCESS", "created_at": datetime.utcnow().isoformat()
                            }).execute()
                            success_count += 1
                            processed_since_break += 1
                            await asyncio.sleep(random.uniform(4.0, 10.0))

                        except Exception as e:
                            err = str(e)
                            if "FloodWait" in err or "SlowMode" in err:
                                next_retry_queue.append(item)
                            else:
                                supabase.table('blast_logs').insert({
                                    "user_id": user_id, "group_name": item['group_name'], "status": "FAILED",
                                    "error_message": err, "created_at": datetime.utcnow().isoformat()
                                }).execute()
                            processed_since_break += 1
                            await asyncio.sleep(2)

                    return next_retry_queue, success_count

                total_success = 0
                retry_1, s1 = await process_queue(send_queue, 1)
                total_success += s1

                if retry_1:
                    await asyncio.sleep(30)
                    retry_2, s2 = await process_queue(retry_1, 2)
                    total_success += s2
                    if retry_2:
                        await asyncio.sleep(60)
                        _, s3 = await process_queue(retry_2, 3)
                        total_success += s3

                send_telegram_alert(user_id, f"✅ **Jadwal Selesai!**\nTotal Terkirim: {total_success}")
                save_notification(user_id, 'Jadwal Blast Selesai', f'Total pesan terkirim: {total_success}', 'success')

            finally:
                if client:
                    await client.disconnect()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_async_send())
        loop.close()

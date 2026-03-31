import re
import os
import json
import random
import logging
import asyncio
import threading
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, Response, stream_with_context
from werkzeug.utils import secure_filename
from decorators import login_required
from models.user import get_dashboard_context, get_active_client
from models.template import MessageTemplateManager
from extensions import supabase, broadcast_states, decrypt_session
from services.helpers import run_async, allowed_file, send_telegram_alert, save_notification
from config import API_ID, API_HASH
from telethon import TelegramClient, utils
from telethon.sessions import StringSession

logger = logging.getLogger("BlastPro_Core")

broadcast_bp = Blueprint('broadcast', __name__)


def process_spintax(text):
    if not text:
        return ""
    pattern = r'\{([^{}]+)\}'
    while True:
        match = re.search(pattern, text)
        if not match:
            break
        options = match.group(1).split('|')
        choice = random.choice(options)
        text = text[:match.start()] + choice + text[match.end():]
    return text


def parse_telegram_link(link):
    link = link.replace('https://t.me/', '').replace('http://t.me/', '').replace('t.me/', '')
    parts = [p for p in link.split('/') if p.strip()]

    if not parts:
        return None, None

    if parts[0] == 'c' and len(parts) >= 3:
        chat_id_str = parts[1]
        msg_id_str = parts[-1]
        try:
            chat_id = int(f"-100{chat_id_str}")
            msg_id = int(msg_id_str)
            return chat_id, msg_id
        except (ValueError, TypeError):
            return None, None

    elif len(parts) >= 2:
        username = parts[0]
        msg_id_str = parts[-1]
        try:
            msg_id = int(msg_id_str)
            return username, msg_id
        except (ValueError, TypeError):
            return None, None

    return None, None


@broadcast_bp.route('/dashboard/broadcast')
@login_required
def dashboard_broadcast():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    crm_count = 0
    templates = []
    accounts = []
    selected_ids = ""
    count_selected = 0

    if not supabase:
        from local_data import get_local_accounts, get_local_crm_users
        accounts = get_local_accounts()
        templates = MessageTemplateManager.get_templates(user.id)
        crm_count = len(get_local_crm_users())
    else:
        try:
            crm_res = supabase.table('tele_users').select("id", count='exact', head=True).eq('owner_id', user.id).execute()
            crm_count = crm_res.count if crm_res.count else 0
            templates = MessageTemplateManager.get_templates(user.id)
            acc_res = supabase.table('telegram_accounts').select("*").eq('user_id', user.id).eq('is_active', True).execute()
            accounts = acc_res.data if acc_res.data else []
        except Exception as e:
            logger.error(f"Broadcast Page Error: {e}")

    ids_arg = request.args.get('ids')
    if ids_arg:
        selected_ids = ids_arg
        count_selected = len(ids_arg.split(','))

    return render_template('dashboard/broadcast.html',
                           user=user,
                           user_count=crm_count,
                           templates=templates,
                           accounts=accounts,
                           selected_ids=selected_ids,
                           count_selected=count_selected,
                           active_page='broadcast')


@broadcast_bp.route('/api/broadcast/stop', methods=['POST'])
@login_required
def stop_broadcast_api():
    user_id = session['user_id']
    broadcast_states[user_id] = 'stopped'
    return jsonify({'status': 'success', 'message': 'Broadcast stopping...'})


@broadcast_bp.route('/start_broadcast', methods=['POST'])
@login_required
def start_broadcast():
    user_id = session['user_id']
    broadcast_states[user_id] = 'running'

    message_raw = request.form.get('message')
    template_id = request.form.get('template_id')
    selected_ids_str = request.form.get('selected_ids')
    target_option = request.form.get('target_option')
    sender_phone_req = request.form.get('sender_phone')
    image_file = request.files.get('image')

    source_media = None
    final_message_template = message_raw

    if template_id:
        tmpl = MessageTemplateManager.get_template_by_id(template_id)
        if tmpl:
            if not final_message_template:
                final_message_template = tmpl['message_text']
            if tmpl.get('source_chat_id') and tmpl.get('source_message_id'):
                source_media = {'chat': int(tmpl['source_chat_id']), 'id': int(tmpl['source_message_id'])}

    if not final_message_template and not source_media:
        return jsonify({"error": "Konten pesan tidak boleh kosong."})

    manual_image_path = None
    if image_file and allowed_file(image_file.filename):
        from flask import current_app
        filename = secure_filename(f"blast_{user_id}_{int(__import__('time').time())}_{image_file.filename}")
        manual_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image_file.save(manual_image_path)

    if not supabase:
        return jsonify({"error": "Database tidak terhubung. Hubungkan Supabase untuk mulai broadcast."})

    targets_raw = []
    try:
        if target_option == 'selected' and selected_ids_str:
            target_ids = [int(x) for x in selected_ids_str.split(',') if x.strip().isdigit()]
            if target_ids:
                res = supabase.table('tele_users').select("*").in_('user_id', target_ids).eq('owner_id', user_id).execute()
                targets_raw = res.data
        else:
            res = supabase.table('tele_users').select("*").eq('owner_id', user_id).limit(5000).execute()
            targets_raw = res.data
    except Exception as e:
        logger.error(f"Broadcast fetch targets error: {e}")
        return jsonify({"error": f"Gagal mengambil data target: {str(e)}"})

    if not targets_raw:
        return jsonify({"error": "Target audiens kosong."})

    unique_targets = {}
    for t in targets_raw:
        unique_targets[t['user_id']] = t
    targets = list(unique_targets.values())

    def generate():
        yield json.dumps({"type": "start", "total": len(targets)}) + "\n"
        success_count = 0
        fail_count = 0

        async def _engine():
            nonlocal success_count, fail_count
            pending_logs = []
            client = None
            try:
                if sender_phone_req and sender_phone_req != 'auto':
                    acc_res = supabase.table('telegram_accounts').select("session_string")\
                        .eq('user_id', user_id).eq('phone_number', sender_phone_req).eq('is_active', True).execute()
                    if acc_res.data:
                        client = TelegramClient(StringSession(decrypt_session(acc_res.data[0]['session_string'])), API_ID, API_HASH, sequential_updates=True)
                        await client.connect()
                    else:
                        yield json.dumps({"type": "error", "msg": f"Akun {sender_phone_req} mati."}) + "\n"
                        return
                else:
                    client = await get_active_client(user_id)

                if not client or not await client.is_user_authorized():
                    yield json.dumps({"type": "error", "msg": "Gagal koneksi ke Telegram."}) + "\n"
                    return

                cloud_msg_obj = None
                if source_media:
                    try:
                        cloud_msg_obj = await client.get_messages(source_media['chat'], ids=source_media['id'])
                    except Exception as e:
                        logger.warning(f"Gagal load cloud message: {e}")

                for idx, tgt in enumerate(targets):
                    if broadcast_states.get(user_id) == 'stopped':
                        yield json.dumps({"type": "error", "msg": "⛔ Broadcast Dihentikan Paksa."}) + "\n"
                        break

                    if idx > 0 and idx % 40 == 0:
                        rest_time = random.randint(120, 240)
                        yield json.dumps({
                            "type": "progress", "current": idx, "total": len(targets),
                            "status": "warning", "log": f"☕ Istirahat {rest_time}s (Mencegah Limit)...",
                            "success": success_count, "failed": fail_count
                        }) + "\n"
                        for _ in range(rest_time):
                            if broadcast_states.get(user_id) == 'stopped':
                                break
                            await asyncio.sleep(1)
                            yield " \n"

                    u_name = tgt.get('first_name') or "Kak"
                    t_id = int(tgt['user_id'])
                    t_username = tgt.get('username')
                    personalized_msg = final_message_template.replace("{name}", u_name) if final_message_template else ""
                    personalized_msg = process_spintax(personalized_msg)

                    log_status = "FAILED"
                    error_msg = None
                    ui_log = ""
                    ui_status = "failed"
                    entity = None

                    try:
                        try:
                            entity = await client.get_input_entity(t_id)
                        except ValueError:
                            if t_username:
                                try:
                                    entity = await client.get_input_entity(t_username)
                                except Exception as inner_e:
                                    raise Exception(f"Username tidak valid atau akun dikunci: {inner_e}")
                            else:
                                raise Exception("Bukan mutual contact dan tidak punya Username.")

                        if not entity:
                            raise Exception("Entity tidak ditemukan.")

                        async with client.action(entity, 'typing'):
                            await asyncio.sleep(random.uniform(1.5, 4.5))

                        if cloud_msg_obj:
                            await client.send_message(entity, cloud_msg_obj)
                        elif manual_image_path:
                            await client.send_file(entity, manual_image_path, caption=personalized_msg)
                        else:
                            await client.send_message(entity, personalized_msg)

                        success_count += 1
                        log_status = "SUCCESS"
                        ui_log = f"Terkirim ke {u_name}"
                        ui_status = "success"

                    except Exception as e:
                        fail_count += 1
                        error_msg = str(e)
                        if "Could not find the input entity" in error_msg or "Cannot find any entity" in error_msg or "Bukan mutual contact" in error_msg:
                            ui_log = f"Gagal: Butuh chat manual/Username untuk {u_name[:10]}"
                            error_msg = "Telegram memblokir pengiriman ke ID baru tanpa username."
                        elif "FloodWait" in error_msg:
                            wait_sec = int(re.search(r'\d+', error_msg).group()) if re.search(r'\d+', error_msg) else 60
                            ui_log = "Gagal: Terkena Limit Telegram (FloodWait)."
                            yield json.dumps({"type": "progress", "log": f"⏳ Telegram limit, istirahat {wait_sec}s...", "status": "warning"}) + "\n"
                            for _ in range(wait_sec):
                                if broadcast_states.get(user_id) == 'stopped':
                                    break
                                await asyncio.sleep(1)
                                yield " \n"
                        else:
                            ui_log = f"Gagal: {error_msg[:20]}..."

                    pending_logs.append({
                        "user_id": user_id,
                        "group_name": f"{u_name} (User)",
                        "group_id": str(t_id),
                        "status": log_status,
                        "error_message": error_msg,
                        "created_at": datetime.utcnow().isoformat()
                    })

                    # Batch insert setiap 20 log untuk mengurangi beban DB
                    if len(pending_logs) >= 20:
                        try:
                            supabase.table('blast_logs').insert(pending_logs).execute()
                            pending_logs.clear()
                        except Exception as _log_err:
                            logger.warning(f"Batch log insert failed: {_log_err}")

                    yield json.dumps({
                        "type": "progress",
                        "current": idx + 1,
                        "total": len(targets),
                        "status": ui_status,
                        "log": ui_log,
                        "success": success_count,
                        "failed": fail_count
                    }) + "\n"

                    delay = random.uniform(5.0, 12.0)
                    for _ in range(int(delay)):
                        if broadcast_states.get(user_id) == 'stopped':
                            break
                        await asyncio.sleep(1)
                        yield " \n"

            except Exception as e:
                yield json.dumps({"type": "error", "msg": f"System Error: {str(e)}"}) + "\n"

            finally:
                # Flush sisa log yang belum di-insert (batch terakhir)
                if pending_logs:
                    try:
                        supabase.table('blast_logs').insert(pending_logs).execute()
                    except Exception as _log_err:
                        logger.warning(f"Final log flush failed: {_log_err}")

                if client:
                    await client.disconnect()
                if manual_image_path and os.path.exists(manual_image_path):
                    try:
                        os.remove(manual_image_path)
                    except OSError as _e:
                        logger.warning(f'Temp image cleanup failed: {_e}')

                if success_count > 0 or fail_count > 0:
                    report_msg = (
                        f"🚀 **BROADCAST SELESAI!**\n"
                        f"─────────────────\n"
                        f"✅ **Berhasil:** {success_count}\n"
                        f"❌ **Gagal:** {fail_count}\n"
                        f"📊 **Total:** {success_count + fail_count}\n"
                        f"─────────────────\n"
                        f"_Cek Log di Dashboard untuk detail error._"
                    )
                    threading.Thread(
                        target=send_telegram_alert,
                        args=(user_id, report_msg, True)
                    ).start()
                    threading.Thread(
                        target=save_notification,
                        args=(user_id, 'Broadcast Selesai',
                              f'Berhasil: {success_count} | Gagal: {fail_count} | Total: {success_count + fail_count}',
                              'success' if success_count > 0 else 'warning')
                    ).start()

                yield json.dumps({"type": "done", "success": success_count, "failed": fail_count}) + "\n"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            runner = _engine()
            while True:
                try:
                    yield loop.run_until_complete(runner.__anext__())
                except StopAsyncIteration:
                    break
        except GeneratorExit:
            logger.warning(f"Client disconnected during broadcast (User: {user_id}).")
            broadcast_states[user_id] = 'stopped'
        finally:
            loop.run_until_complete(runner.aclose())
            loop.close()

    return Response(stream_with_context(generate()), mimetype='application/json')


@broadcast_bp.route('/scan_groups_api')
@login_required
def scan_groups_api():
    user_id = session.get('user_id')
    target_phone = request.args.get('phone')

    if user_id is None:
        return jsonify({"status": "error", "message": "User not authenticated."}), 401

    async def _scan():
        from telethon import utils as tele_utils, types, functions
        from telethon.tl.types import InputPeerChannel

        GetForumTopicsRequest = None
        if hasattr(functions.channels, 'GetForumTopicsRequest'):
            GetForumTopicsRequest = functions.channels.GetForumTopicsRequest
        elif hasattr(functions.messages, 'GetForumTopicsRequest'):
            GetForumTopicsRequest = functions.messages.GetForumTopicsRequest
        elif hasattr(functions.channels, 'GetForumTopics'):
            GetForumTopicsRequest = functions.channels.GetForumTopics

        HAS_RAW_API = GetForumTopicsRequest is not None

        client = None
        if target_phone:
            try:
                res = supabase.table('telegram_accounts').select("session_string")\
                    .eq('user_id', user_id).eq('phone_number', target_phone).eq('is_active', True).execute()
                if res.data:
                    client = TelegramClient(StringSession(decrypt_session(res.data[0]['session_string'])), API_ID, API_HASH)
                    await client.connect()
            except Exception as e:
                logger.error(f"Connect Error: {e}")

        if not client:
            client = await get_active_client(user_id)

        if not client:
            return jsonify({"status": "error", "message": "Tidak ada akun Telegram yang terhubung."})

        groups = []
        stats = {'groups': 0, 'forums': 0, 'errors': 0, 'skipped': 0, 'topics_found': 0}

        try:
            async for dialog in client.iter_dialogs(limit=500):
                try:
                    if not dialog.is_group:
                        stats['skipped'] += 1
                        continue

                    entity = dialog.entity
                    real_id = tele_utils.get_peer_id(entity)
                    member_count = getattr(entity, 'participants_count', 0)
                    username = getattr(entity, 'username', None)
                    is_forum = getattr(entity, 'forum', False)

                    all_topics = []
                    if is_forum:
                        stats['forums'] += 1
                        if HAS_RAW_API:
                            try:
                                access_hash = getattr(entity, 'access_hash', None)
                                if access_hash:
                                    input_channel = InputPeerChannel(channel_id=entity.id, access_hash=access_hash)
                                else:
                                    input_channel = await client.get_input_entity(real_id)

                                offset_id, offset_date, offset_topic = 0, 0, 0
                                for page in range(5):
                                    req = GetForumTopicsRequest(
                                        input_channel, q='',
                                        offset_date=offset_date,
                                        offset_id=offset_id,
                                        offset_topic=offset_topic,
                                        limit=100
                                    )
                                    res = await client(req)
                                    if not res.topics:
                                        break
                                    for t in res.topics:
                                        t_id = getattr(t, 'id', None)
                                        if t_id:
                                            t_title = getattr(t, 'title', '')
                                            if isinstance(t, types.ForumTopicDeleted):
                                                t_title = f"(Deleted) #{t_id}"
                                            elif not t_title:
                                                t_title = f"Topic #{t_id}"
                                            if t_id == 1 and ("Topic #1" in t_title or not t_title):
                                                t_title = "General 📌"
                                            all_topics.append({'id': t_id, 'title': t_title})
                                            stats['topics_found'] += 1
                                    last = res.topics[-1]
                                    offset_id = getattr(last, 'id', 0)
                                    offset_date = getattr(last, 'date', 0)
                                    await asyncio.sleep(0.2)

                                all_topics.sort(key=lambda x: x['id'])
                                if not any(t['id'] == 1 for t in all_topics):
                                    all_topics.insert(0, {'id': 1, 'title': 'General (Topik Utama) 📌'})

                            except Exception as forum_e:
                                logger.error(f"Forum Scan Error {dialog.name}: {forum_e}")
                                all_topics = [{'id': 1, 'title': 'General (Fallback - Scan Error)'}]
                        else:
                            all_topics = [{'id': 1, 'title': 'General (Fallback - API Missing)'}]
                    else:
                        stats['groups'] += 1

                    g_data = {
                        'id': real_id,
                        'name': dialog.name,
                        'is_forum': is_forum,
                        'username': f"@{username}" if username else None,
                        'members': member_count,
                        'topics': all_topics
                    }
                    groups.append(g_data)

                except Exception as group_e:
                    logger.warning(f"Skip Group Error: {group_e}")
                    stats['errors'] += 1
                    continue

        except Exception as e:
            logger.critical(f"FATAL SCAN ERROR: {e}")
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            await client.disconnect()

        return jsonify({'status': 'success', 'data': groups, 'meta': stats})

    return run_async(_scan())


@broadcast_bp.route('/save_bulk_targets', methods=['POST'])
@login_required
def save_bulk_targets():
    user_id = session['user_id']
    data = request.json
    targets = data.get('targets', [])
    source_phone = data.get('source_phone')
    template_name = data.get('template_name', 'Scan Result ' + datetime.now().strftime('%d/%m'))

    if not targets:
        return jsonify({'status': 'error', 'message': 'Tidak ada grup yang dipilih'})

    try:
        source_name = None
        if source_phone:
            acc_data = supabase.table('telegram_accounts').select("first_name").eq('phone_number', source_phone).eq('user_id', user_id).execute()
            if acc_data.data:
                source_name = acc_data.data[0]['first_name']

        final_data = []
        for t in targets:
            final_data.append({
                'user_id': user_id,
                'group_name': t['group_name'],
                'group_id': str(t['group_id']),
                'topic_ids': ",".join(map(str, t['topic_ids'])) if t.get('topic_ids') else None,
                'created_at': datetime.now().isoformat(),
                'source_phone': source_phone,
                'source_name': source_name,
                'template_name': template_name
            })

        supabase.table('blast_targets').insert(final_data).execute()
        return jsonify({'status': 'success', 'message': 'Database berhasil disimpan!'})

    except Exception as e:
        logger.error(f"Error saving targets: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


@broadcast_bp.route('/api/fetch_message', methods=['POST'])
@login_required
def fetch_telegram_message():
    user_id = session['user_id']
    link = request.json.get('link')
    if not link:
        return jsonify({'status': 'error', 'message': 'Link kosong.'})

    async def _fetch():
        client = await get_active_client(user_id)
        if not client:
            return jsonify({'status': 'error', 'message': 'Telegram disconnected.'})
        try:
            entity, msg_id = parse_telegram_link(link)
            if not entity or not msg_id:
                return jsonify({'status': 'error', 'message': 'Link tidak valid.'})
            msg = await client.get_messages(entity, ids=msg_id)
            if not msg:
                return jsonify({'status': 'error', 'message': 'Pesan tidak ditemukan.'})
            return jsonify({
                'status': 'success', 'text': msg.text or "",
                'has_media': True if msg.media else False,
                'source_chat_id': str(utils.get_peer_id(msg.peer_id)), 'source_message_id': msg.id
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            await client.disconnect()

    return run_async(_fetch())


@broadcast_bp.route('/api/get_crm_users', methods=['GET'])
def get_crm_users_api():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Sesi Anda telah berakhir, silakan login ulang.'}), 401

    user_id = session['user_id']
    source = request.args.get('source', 'all')
    search_query = request.args.get('q', '').strip()

    try:
        query = supabase.table('tele_users').select("user_id, username, first_name").eq('owner_id', user_id)
        if source != 'all':
            query = query.eq('source_phone', source)
        if search_query:
            if search_query.isdigit():
                search_filter = f"user_id.eq.{search_query},username.ilike.%{search_query}%,first_name.ilike.%{search_query}%"
                query = query.or_(search_filter)
            else:
                search_filter = f"username.ilike.%{search_query}%,first_name.ilike.%{search_query}%"
                query = query.or_(search_filter)

        res = query.order('last_interaction', desc=True).limit(5000).execute()
        return jsonify({'status': 'success', 'users': res.data if res.data else []})

    except Exception as e:
        logger.error(f"API Get CRM Users Error: {e}")
        return jsonify({'status': 'error', 'message': 'Gagal mengambil data dari database.'}), 500

import logging
import time
import threading
import base64
import uuid
import asyncio
from io import BytesIO
from datetime import datetime
from flask import Blueprint, request, session, jsonify
from decorators import login_required
from extensions import supabase, login_states, qr_states, encrypt_session, decrypt_session
from models.user import get_user_data
from services.helpers import run_async, get_max_accounts
from config import API_ID, API_HASH
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
import qrcode

logger = logging.getLogger("BlastPro_Core")

connection_bp = Blueprint('connection', __name__)


@connection_bp.route('/api/connect/send_code', methods=['POST'])
@login_required
def send_code():
    phone = request.json.get('phone')
    user_id = session['user_id']

    if not phone:
        return jsonify({'status': 'error', 'message': 'Nomor HP wajib diisi.'})

    try:
        user_data = get_user_data(user_id)
        plan_tier = user_data.plan_tier if user_data else 'STARTER'
        max_accounts = get_max_accounts(plan_tier)

        res = supabase.table('telegram_accounts').select("id", count='exact', head=True).eq('user_id', user_id).execute()
        current_count = res.count if res.count else 0

        check_exist = supabase.table('telegram_accounts').select("id").eq('user_id', user_id).eq('phone_number', phone).execute()
        is_existing_number = True if check_exist.data else False

        if not is_existing_number and current_count >= max_accounts:
            return jsonify({
                'status': 'limit_reached',
                'message': f'Batas Maksimal {max_accounts} Akun Tercapai (Paket {plan_tier.upper()})! Silakan Upgrade Paket.'
            })
    except Exception as e:
        logger.error(f"Limit Check Error: {e}")

    current_time = time.time()
    if user_id in login_states:
        last_req = login_states[user_id].get('last_otp_req', 0)
        if current_time - last_req < 60:
            remaining = int(60 - (current_time - last_req))
            return jsonify({'status': 'cooldown', 'message': f'Tunggu {remaining} detik lagi.'})

    async def _process_send_code():
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                req = await client.send_code_request(phone)
                temp_session_str = encrypt_session(client.session.save())

                data = {
                    'user_id': user_id,
                    'phone_number': phone,
                    'session_string': temp_session_str,
                    'targets': req.phone_code_hash,
                    'is_active': False,
                    'created_at': datetime.utcnow().isoformat()
                }
                supabase.table('telegram_accounts').upsert(data, on_conflict="user_id, phone_number").execute()
                login_states[user_id] = {'last_otp_req': current_time, 'pending_phone': phone}
                return jsonify({'status': 'success', 'message': 'Kode OTP terkirim!'})
            else:
                return jsonify({'status': 'error', 'message': 'Nomor ini aneh (Authorized but not local).'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Telegram Error: {str(e)}'})
        finally:
            await client.disconnect()

    return run_async(_process_send_code())


@connection_bp.route('/api/connect/verify_code', methods=['POST'])
@login_required
def verify_code():
    user_id = session['user_id']
    otp = request.json.get('otp')
    pw = request.json.get('password')

    db_session = None
    db_hash = None
    db_phone = None

    try:
        res = supabase.table('telegram_accounts').select("*").eq('user_id', user_id).eq('is_active', False).not_.is_('targets', 'null').neq('targets', '').limit(1).execute()
        if not res.data:
            return jsonify({'status': 'error', 'message': 'Sesi kadaluarsa. Kirim ulang OTP.'})
        row = res.data[0]
        db_session = decrypt_session(row['session_string'])
        db_phone = row['phone_number']
        db_hash = row['targets']
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Database Error: {str(e)}'})

    async def _process_verify():
        client = TelegramClient(StringSession(db_session), API_ID, API_HASH)
        await client.connect()
        try:
            try:
                await client.sign_in(db_phone, otp, phone_code_hash=db_hash)
            except errors.SessionPasswordNeededError:
                if not pw:
                    return jsonify({'status': '2fa', 'message': 'Akun dilindungi 2FA. Masukkan Password.'})
                await client.sign_in(password=pw)

            me = await client.get_me()
            final_session = encrypt_session(client.session.save())
            update_data = {
                'session_string': final_session,
                'is_active': True,
                'targets': '[]',
                'created_at': datetime.utcnow().isoformat(),
                'first_name': me.first_name or '',
                'last_name': me.last_name or '',
                'username': me.username or ''
            }
            supabase.table('telegram_accounts').update(update_data).eq('user_id', user_id).eq('phone_number', db_phone).execute()
            return jsonify({'status': 'success', 'message': f'Berhasil login sebagai {me.first_name}!'})

        except errors.PhoneCodeInvalidError:
            return jsonify({'status': 'error', 'message': 'Kode OTP salah.'})
        except Exception as e:
            logger.error(f"Login Failed: {e}")
            return jsonify({'status': 'error', 'message': f'Gagal: {str(e)}'})
        finally:
            await client.disconnect()

    try:
        return run_async(_process_verify())
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@connection_bp.route('/api/connect/disconnect', methods=['POST'])
@login_required
def disconnect_account():
    phone = request.json.get('phone')
    user_id = session['user_id']
    try:
        supabase.table('telegram_accounts').delete().eq('user_id', user_id).eq('phone_number', phone).execute()
        return jsonify({'status': 'success', 'message': f'Akun {phone} berhasil dihapus.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


def qr_worker(user_id, session_uuid):
    logger.info(f"[QR_THREAD] [{session_uuid}]: Worker Started")

    async def _process():
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()

        try:
            if not await client.is_user_authorized():
                qr_login = await client.qr_login()
                qr_states[session_uuid]['qr_url'] = qr_login.url
                qr_states[session_uuid]['status'] = 'waiting'

                try:
                    logger.info(f"[QR_THREAD] [{session_uuid}]: Waiting scan...")
                    await qr_login.wait(timeout=120)

                    try:
                        me = await client.get_me()
                        final_session = encrypt_session(client.session.save())
                        qr_states[session_uuid]['user_data'] = {
                            'session': final_session,
                            'phone': f"+{me.phone}",
                            'first_name': me.first_name,
                            'last_name': me.last_name,
                            'username': me.username
                        }
                        qr_states[session_uuid]['status'] = 'success'
                        logger.info(f"[QR_THREAD] [{session_uuid}]: Login Success (No 2FA)")

                    except errors.SessionPasswordNeededError:
                        logger.info(f"[QR_THREAD] [{session_uuid}]: 2FA REQUIRED!")
                        qr_states[session_uuid]['status'] = '2fa_required'

                        password_received = False
                        for _ in range(240):
                            if 'password_input' in qr_states[session_uuid]:
                                pw = qr_states[session_uuid]['password_input']
                                try:
                                    await client.sign_in(password=pw)
                                    me = await client.get_me()
                                    final_session = encrypt_session(client.session.save())
                                    qr_states[session_uuid]['user_data'] = {
                                        'session': final_session,
                                        'phone': f"+{me.phone}",
                                        'first_name': me.first_name,
                                        'last_name': me.last_name,
                                        'username': me.username
                                    }
                                    qr_states[session_uuid]['status'] = 'success'
                                    password_received = True
                                    break
                                except Exception as pw_e:
                                    logger.warning(f"[QR_THREAD] [{session_uuid}]: Wrong Password: {pw_e}")
                                    qr_states[session_uuid]['status'] = 'error'
                                    qr_states[session_uuid]['error_msg'] = "Password Salah!"
                                    password_received = True
                                    break
                            await asyncio.sleep(0.5)

                        if not password_received:
                            qr_states[session_uuid]['status'] = 'expired'

                except asyncio.TimeoutError:
                    qr_states[session_uuid]['status'] = 'expired'
            else:
                qr_states[session_uuid]['status'] = 'error'
                qr_states[session_uuid]['error_msg'] = "Client already auth?"

        except Exception as e:
            err = str(e)
            logger.error(f"[QR_THREAD] [{session_uuid}]: CRITICAL ERROR: {err}")
            qr_states[session_uuid]['status'] = 'error'
            qr_states[session_uuid]['error_msg'] = err
        finally:
            await client.disconnect()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_process())
    loop.close()


@connection_bp.route('/api/connect/get_qr', methods=['POST'])
@login_required
def get_qr_code():
    user_id = session['user_id']

    try:
        user_data = get_user_data(user_id)
        plan_tier = user_data.plan_tier if user_data else 'STARTER'
        max_accounts = get_max_accounts(plan_tier)

        res = supabase.table('telegram_accounts').select("id", count='exact', head=True).eq('user_id', user_id).execute()
        if (res.count or 0) >= max_accounts:
            return jsonify({
                'status': 'limit_reached',
                'message': f'Batas Maksimal {max_accounts} Akun Tercapai (Paket {plan_tier.upper()})! Silakan Upgrade Paket.'
            })
    except Exception as e:
        logger.error(f"Limit Check QR Error: {e}")

    session_uuid = str(uuid.uuid4())
    qr_states[session_uuid] = {'status': 'initializing', 'qr_url': None}

    t = threading.Thread(target=qr_worker, args=(user_id, session_uuid))
    t.daemon = True
    t.start()

    for _ in range(50):
        if qr_states[session_uuid].get('qr_url'):
            break
        time.sleep(0.1)

    if not qr_states[session_uuid].get('qr_url'):
        return jsonify({'status': 'error', 'message': 'Timeout koneksi Telegram.'})

    url = qr_states[session_uuid]['qr_url']
    img = qrcode.make(url)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return jsonify({
        'status': 'success',
        'qr_image': f"data:image/png;base64,{img_str}",
        'session_uuid': session_uuid
    })


@connection_bp.route('/api/connect/submit_2fa', methods=['POST'])
@login_required
def submit_2fa_qr():
    session_uuid = request.json.get('session_uuid')
    password = request.json.get('password')

    if session_uuid in qr_states:
        qr_states[session_uuid]['password_input'] = password
        return jsonify({'status': 'success'})

    return jsonify({'status': 'error', 'message': 'Sesi QR hilang/kadaluarsa'})


@connection_bp.route('/api/connect/check_qr', methods=['POST'])
@login_required
def check_qr_status():
    session_uuid = request.json.get('session_uuid')
    user_id = session['user_id']

    if not session_uuid or session_uuid not in qr_states:
        return jsonify({'status': 'expired', 'message': 'QR Expired.'})

    state = qr_states[session_uuid]
    status = state.get('status')

    if status == 'success':
        u_data = state['user_data']
        db_data = {
            'user_id': user_id,
            'phone_number': u_data['phone'],
            'session_string': u_data['session'],
            'first_name': u_data['first_name'] or '',
            'last_name': u_data['last_name'] or '',
            'username': u_data['username'] or '',
            'is_active': True,
            'targets': '[]',
            'created_at': datetime.utcnow().isoformat()
        }
        try:
            supabase.table('telegram_accounts').upsert(db_data, on_conflict="user_id, phone_number").execute()
        except Exception as e:
            logger.error(f"QR Save Session Error: {e}")
            return jsonify({'status': 'error', 'message': f'Login OK tapi gagal simpan sesi: {str(e)}'})
        del qr_states[session_uuid]
        return jsonify({'status': 'success', 'message': f"Login Berhasil: {u_data['first_name']}"})

    elif status == '2fa_required':
        return jsonify({'status': '2fa'})
    elif status == 'expired':
        return jsonify({'status': 'expired'})
    elif status == 'error':
        return jsonify({'status': 'error', 'message': state.get('error_msg', 'Unknown Error')})
    else:
        return jsonify({'status': 'waiting'})

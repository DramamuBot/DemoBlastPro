import math
import csv
import io
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from decorators import login_required
from models.user import get_dashboard_context
from extensions import supabase
from services.helpers import run_async
from config import API_ID, API_HASH
from extensions import decrypt_session
from telethon import TelegramClient
from telethon.sessions import StringSession

logger = logging.getLogger("BlastPro_Core")

crm_bp = Blueprint('crm', __name__)


@crm_bp.route('/dashboard/crm')
@login_required
def dashboard_crm():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    accounts = []
    active_phones = []

    if not supabase:
        from local_data import get_local_accounts
        accounts = get_local_accounts()
        active_phones = [acc['phone_number'] for acc in accounts]
    else:
        try:
            acc_res = supabase.table('telegram_accounts').select("*")\
                .eq('user_id', user.id).eq('is_active', True)\
                .order('created_at', desc=True).execute()
            accounts = acc_res.data if acc_res.data else []
            active_phones = [acc['phone_number'] for acc in accounts]
        except Exception as e:
            logger.error(f"Fetch Accounts Error: {e}")

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search_query = request.args.get('q', '').strip()
    current_source = request.args.get('source', 'all')
    start = (page - 1) * per_page
    end = start + per_page - 1

    crm_users = []
    total_users = 0
    total_pages = 0

    if not supabase:
        from local_data import get_local_crm_users
        all_local = get_local_crm_users()
        if search_query:
            all_local = [u for u in all_local if
                         search_query.lower() in (u.get('first_name') or '').lower() or
                         search_query.lower() in (u.get('username') or '').lower() or
                         search_query in str(u.get('user_id', ''))]
        if current_source != 'all':
            all_local = [u for u in all_local if u.get('source_phone') == current_source]
        total_users = len(all_local)
        crm_users = all_local[start:start + per_page]
        total_pages = math.ceil(total_users / per_page) if per_page > 0 else 0

    if supabase:
        try:
            query = supabase.table('tele_users').select("*", count='exact').eq('owner_id', user.id)

            if current_source != 'all':
                query = query.eq('source_phone', current_source)
            # When viewing 'all', show ALL contacts owned by user regardless of active phones

            if search_query:
                safe_search = search_query.replace("'", "''").replace(",", "").replace("%", "\\%")
                if search_query.isdigit():
                    search_filter = f"user_id.eq.{search_query},username.ilike.%{safe_search}%,first_name.ilike.%{safe_search}%"
                    query = query.or_(search_filter)
                else:
                    search_filter = f"username.ilike.%{safe_search}%,first_name.ilike.%{safe_search}%"
                    query = query.or_(search_filter)

            res = query.order('last_interaction', desc=True).range(start, end).execute()
            crm_users = res.data if res.data else []
            total_users = res.count if res.count else 0
            total_pages = math.ceil(total_users / per_page) if per_page > 0 else 0

        except Exception as e:
            logger.error(f"CRM Data Error: {e}")
            crm_users = []

    return render_template('dashboard/crm.html',
                           user=user,
                           crm_users=crm_users,
                           user_count=total_users,
                           total_users=total_users,
                           current_page=page,
                           total_pages=total_pages,
                           per_page=per_page,
                           search_query=search_query,
                           active_page='crm',
                           accounts=accounts,
                           current_source=current_source)


@crm_bp.route('/import_crm_api', methods=['POST'])
@login_required
def import_crm_api():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    source_phone = request.form.get('source_phone')
    group_id = request.form.get('group_id')

    if not source_phone or not group_id:
        flash('Pilih akun & grup terlebih dahulu.', 'danger')
        return redirect(url_for('crm.dashboard_crm'))

    try:
        acc_res = supabase.table('telegram_accounts').select("session_string")\
            .eq('user_id', user.id).eq('phone_number', source_phone).eq('is_active', True).execute()
        if not acc_res.data:
            flash('Akun tidak ditemukan.', 'danger')
            return redirect(url_for('crm.dashboard_crm'))

        session_str = decrypt_session(acc_res.data[0]['session_string'])
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('crm.dashboard_crm'))

    total_imported = 0
    error_msg = None

    async def _import_members():
        nonlocal total_imported, error_msg
        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                error_msg = "Sesi tidak valid."
                return

            from telethon.tl.functions.channels import GetParticipantsRequest
            from telethon.tl.types import ChannelParticipantsSearch

            entity = await client.get_entity(int(group_id))
            input_channel = await client.get_input_entity(entity)

            all_members = []
            offset = 0
            while True:
                participants = await client(GetParticipantsRequest(
                    input_channel, ChannelParticipantsSearch(''),
                    offset=offset, limit=200, hash=0
                ))
                if not participants.users:
                    break
                all_members.extend(participants.users)
                offset += len(participants.users)
                if len(participants.users) < 200:
                    break

            upsert_data = []
            for m in all_members:
                if m.bot or m.deleted:
                    continue
                phone = f"+{m.phone}" if m.phone else None
                u_data = {
                    'owner_id': user.id,
                    'user_id': m.id,
                    'source_phone': source_phone,
                    'username': m.username or '',
                    'first_name': m.first_name or '',
                    'last_name': m.last_name or '',
                    'phone': phone,
                    'last_interaction': datetime.utcnow().isoformat()
                }
                upsert_data.append(u_data)

            if upsert_data:
                for i in range(0, len(upsert_data), 100):
                    chunk = upsert_data[i:i+100]
                    supabase.table('tele_users').upsert(chunk, on_conflict="owner_id, user_id").execute()
                total_imported = len(upsert_data)

        except Exception as e:
            error_msg = str(e)
        finally:
            await client.disconnect()

    run_async(_import_members())

    if error_msg:
        flash(f'Gagal import: {error_msg}', 'danger')
    else:
        flash(f'✅ Berhasil import {total_imported} anggota.', 'success')

    return redirect(url_for('crm.dashboard_crm'))


@crm_bp.route('/import_crm_csv', methods=['POST'])
@login_required
def import_crm_csv():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    csv_file = request.files.get('csv_file')
    if not csv_file or not csv_file.filename.endswith('.csv'):
        flash('File harus format .csv!', 'danger')
        return redirect(url_for('crm.dashboard_crm'))

    try:
        stream = io.StringIO(csv_file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)
        rows = []
        for row in reader:
            r = {k.strip(): v.strip() for k, v in row.items()}
            try:
                user_id_val = int(r.get('user_id') or r.get('id') or '0')
            except ValueError:
                continue
            if not user_id_val:
                continue
            rows.append({
                'owner_id': user.id,
                'user_id': user_id_val,
                'username': r.get('username', ''),
                'first_name': r.get('first_name') or r.get('name', ''),
                'last_name': r.get('last_name', ''),
                'phone': r.get('phone', None),
                'source_phone': r.get('source_phone', 'CSV Import'),
                'last_interaction': datetime.utcnow().isoformat()
            })

        if rows:
            for i in range(0, len(rows), 100):
                chunk = rows[i:i+100]
                supabase.table('tele_users').upsert(chunk, on_conflict="owner_id, user_id").execute()
            flash(f'✅ Berhasil import {len(rows)} kontak.', 'success')
        else:
            flash('File CSV kosong atau formatnya salah.', 'danger')

    except Exception as e:
        logger.error(f"CSV Import Error: {e}")
        flash(f'Gagal import CSV: {str(e)}', 'danger')

    return redirect(url_for('crm.dashboard_crm'))


@crm_bp.route('/export_crm_csv')
@login_required
def export_crm_csv():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    if not supabase:
        flash('Fitur export tidak tersedia: Database tidak terhubung.', 'danger')
        return redirect(url_for('crm.dashboard_crm'))

    try:
        data = supabase.table('tele_users').select("*").eq('owner_id', user.id).execute().data or []
    except Exception as e:
        logger.error(f"Export CRM Error: {e}")
        flash(f'Gagal export: {str(e)}', 'danger')
        return redirect(url_for('crm.dashboard_crm'))

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['user_id', 'username', 'first_name', 'last_name', 'phone', 'source_phone'])
    for row in data:
        cw.writerow([
            row.get('user_id', ''),
            row.get('username', ''),
            row.get('first_name', ''),
            row.get('last_name', ''),
            row.get('phone', ''),
            row.get('source_phone', '')
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=crm_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@crm_bp.route('/delete_crm_user', methods=['POST'])
@crm_bp.route('/delete_crm_user/<int:uid>', methods=['GET'])
@login_required
def delete_crm_user(uid=None):
    if uid is None:
        uid = request.form.get('user_id', type=int)
    if not uid:
        flash('ID kontak tidak valid.', 'danger')
        return redirect(url_for('crm.dashboard_crm'))
    if not supabase:
        flash('Fitur hapus tidak tersedia: Database tidak terhubung.', 'danger')
        return redirect(url_for('crm.dashboard_crm'))
    try:
        supabase.table('tele_users').delete().eq('owner_id', session['user_id']).eq('id', uid).execute()
        flash('Kontak dihapus.', 'success')
    except Exception as e:
        flash(f'Gagal menghapus: {str(e)}', 'danger')
    return redirect(url_for('crm.dashboard_crm'))


@crm_bp.route('/delete_crm_user_massal', methods=['POST'])
@login_required
def delete_crm_user_massal():
    user_id = session['user_id']
    ids = []

    if request.is_json:
        data = request.get_json(silent=True) or {}
        ids = data.get('ids', [])
    else:
        raw = request.form.get('user_ids', '')
        ids = [int(x.strip()) for x in raw.split(',') if x.strip().isdigit()]

    if not ids:
        return jsonify({'status': 'error', 'message': 'Tidak ada data yang dipilih.'})

    if not supabase:
        return jsonify({'status': 'error', 'message': 'Database tidak terhubung.'})

    try:
        supabase.table('tele_users').delete().eq('owner_id', user_id).in_('id', ids).execute()
        return jsonify({'status': 'success', 'message': f'{len(ids)} kontak berhasil dihapus.'})
    except Exception as e:
        logger.error(f"Massal delete error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


@crm_bp.route('/api/scan_group_members', methods=['GET'])
@login_required
def scan_group_members_api():
    user_id = session['user_id']
    group_id_raw = request.args.get('group_id')
    source_phone = request.args.get('phone')

    if not group_id_raw or not source_phone:
        return jsonify({'status': 'error', 'message': 'Param kurang lengkap.'})

    try:
        group_id = int(group_id_raw)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Group ID tidak valid.'})

    try:
        acc_res = supabase.table('telegram_accounts').select("session_string")\
            .eq('user_id', user_id).eq('phone_number', source_phone).eq('is_active', True).execute()
        if not acc_res.data:
            return jsonify({'status': 'error', 'message': 'Akun tidak ditemukan.'})
        session_str = decrypt_session(acc_res.data[0]['session_string'])
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

    async def _scan():
        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                return jsonify({'status': 'error', 'message': 'Sesi expired.'})

            from telethon.tl.functions.channels import GetParticipantsRequest
            from telethon.tl.types import ChannelParticipantsSearch

            entity = await client.get_entity(group_id)
            input_channel = await client.get_input_entity(entity)

            all_members = []
            offset = 0
            while True:
                participants = await client(GetParticipantsRequest(
                    input_channel, ChannelParticipantsSearch(''),
                    offset=offset, limit=200, hash=0
                ))
                if not participants.users:
                    break
                all_members.extend(participants.users)
                offset += len(participants.users)
                if len(participants.users) < 200:
                    break

            upsert_data = []
            for m in all_members:
                if m.bot or m.deleted:
                    continue
                phone = f"+{m.phone}" if m.phone else None
                upsert_data.append({
                    'owner_id': user_id,
                    'user_id': m.id,
                    'source_phone': source_phone,
                    'username': m.username or '',
                    'first_name': m.first_name or '',
                    'last_name': m.last_name or '',
                    'phone': phone,
                    'last_interaction': datetime.utcnow().isoformat()
                })

            if upsert_data:
                for i in range(0, len(upsert_data), 100):
                    chunk = upsert_data[i:i+100]
                    supabase.table('tele_users').upsert(chunk, on_conflict="owner_id, user_id").execute()

            return jsonify({'status': 'success', 'total_imported': len(upsert_data)})

        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            await client.disconnect()

    return run_async(_scan())

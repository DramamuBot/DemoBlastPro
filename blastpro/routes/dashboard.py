import math
import json
import uuid
import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from decorators import login_required
from models.user import get_user_data, get_dashboard_context
from models.finance import FinanceManager
from extensions import supabase

logger = logging.getLogger("BlastPro_Core")

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('')
@dashboard_bp.route('/')
@login_required
def overview():
    user = get_dashboard_context(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('⛔ Akun Anda dibekukan oleh Administrator.', 'danger')
        return redirect(url_for('auth.login'))

    if user.is_admin:
        return redirect(url_for('admin.dashboard'))

    uid = user.id
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status_filter = request.args.get('status_filter', 'all')
    date_filter = request.args.get('date_filter', 'all')
    search_target = request.args.get('search_target', '').strip()
    sender_filter = request.args.get('sender_filter', '')
    start = (page - 1) * per_page
    end = start + per_page - 1

    now_utc = datetime.utcnow()
    date_cutoff = None
    if date_filter == 'today':
        date_cutoff = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_filter == '7d':
        date_cutoff = now_utc - timedelta(days=7)
    elif date_filter == '30d':
        date_cutoff = now_utc - timedelta(days=30)

    logs = []
    schedules = []
    targets = []
    accounts_list = []
    total_logs = 0
    total_pages = 0
    stats = {}
    crm_count = 0

    if not supabase:
        from local_data import get_local_blast_logs, get_local_schedules, get_local_targets, get_local_stats, get_local_crm_users, get_local_accounts
        logs = get_local_blast_logs()
        schedules = get_local_schedules()
        targets = get_local_targets()
        stats = get_local_stats()
        crm_count = len(get_local_crm_users())
        accounts_list = get_local_accounts()
        if status_filter == 'success':
            logs = [l for l in logs if l.get('status', '').upper() in ('SUCCESS', 'BERHASIL')]
        elif status_filter == 'failed':
            logs = [l for l in logs if l.get('status', '').upper() not in ('SUCCESS', 'BERHASIL')]
        if date_cutoff:
            logs = [l for l in logs if l.get('created_at', '') >= date_cutoff.isoformat()]
        if search_target:
            kw = search_target.lower()
            logs = [l for l in logs if kw in (l.get('group_name') or l.get('target_name') or '').lower()]
        if sender_filter:
            logs = [l for l in logs if l.get('sender_phone', '') == sender_filter]
        total_logs = len(logs)
        total_pages = 1

    if supabase:
        try:
            accounts_res = supabase.table('telegram_accounts').select("phone_number,first_name").eq('user_id', uid).execute()
            accounts_list = accounts_res.data if accounts_res.data else []

            def _apply_filters(q):
                if status_filter == 'success':
                    q = q.eq('status', 'SUCCESS')
                elif status_filter == 'failed':
                    q = q.neq('status', 'SUCCESS')
                if date_cutoff:
                    q = q.gte('created_at', date_cutoff.isoformat())
                if search_target:
                    q = q.ilike('group_name', f'%{search_target}%')
                if sender_filter:
                    q = q.eq('sender_phone', sender_filter)
                return q

            count_q = _apply_filters(supabase.table('blast_logs').select("id", count='exact', head=True).eq('user_id', uid))
            count_res = count_q.execute()
            total_logs = count_res.count if count_res.count else 0
            total_pages = math.ceil(total_logs / per_page) if per_page else 1

            logs_q = _apply_filters(supabase.table('blast_logs').select("*").eq('user_id', uid))
            logs_raw = logs_q.order('created_at', desc=True).range(start, end).execute().data

            logs = []
            if logs_raw:
                for log in logs_raw:
                    if log.get('created_at'):
                        try:
                            utc_dt = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00'))
                            wib_dt = utc_dt + timedelta(hours=7)
                            log['wib_time'] = wib_dt.strftime('%H:%M:%S')
                            log['wib_date'] = wib_dt.strftime('%Y-%m-%d')
                        except Exception:
                            log['wib_time'] = log['created_at'][11:19] if len(log['created_at']) > 18 else "--:--:--"
                            log['wib_date'] = log['created_at'][:10] if len(log['created_at']) >= 10 else "Unknown"
                    logs.append(log)

            schedules = supabase.table('blast_schedules').select("*").eq('user_id', uid).execute().data
            targets = supabase.table('blast_targets').select("*").eq('user_id', uid).execute().data

            acc_count = supabase.table('telegram_accounts').select("id", count='exact', head=True).eq('user_id', uid).eq('is_active', True).execute().count
            success_blast = supabase.table('blast_logs').select("id", count='exact', head=True).eq('user_id', uid).eq('status', 'SUCCESS').execute().count
            crm_count = supabase.table('tele_users').select("id", count='exact', head=True).eq('owner_id', uid).execute().count

            stats = {
                'connected_accounts': acc_count or 0,
                'total_blast': total_logs,
                'success_rate': int((success_blast / total_logs) * 100) if total_logs > 0 else 0,
                'active_schedules': len([s for s in schedules if s.get('is_active')])
            }
        except Exception as e:
            logger.error(f"Dashboard Data Error: {e}")
            stats = {'connected_accounts': 0, 'total_blast': 0, 'success_rate': 0, 'active_schedules': 0}
            crm_count = 0

    return render_template('dashboard/index.html',
                           user=user,
                           stats=stats,
                           logs=logs,
                           schedules=schedules,
                           targets=targets,
                           accounts_list=accounts_list,
                           current_page=page,
                           total_pages=total_pages,
                           total_logs=total_logs,
                           user_count=crm_count or 0,
                           per_page=per_page,
                           status_filter=status_filter,
                           date_filter=date_filter,
                           search_target=search_target,
                           sender_filter=sender_filter,
                           active_page='home')


@dashboard_bp.route('/connection')
@login_required
def connection():
    user = get_user_data(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    accounts = []
    if not supabase:
        from local_data import get_local_accounts
        accounts = get_local_accounts()
    else:
        try:
            res = supabase.table('telegram_accounts').select("*").eq('user_id', user.id).order('created_at', desc=True).execute()
            accounts = res.data if res.data else []
        except Exception as e:
            logger.error(f"Fetch Accounts Error: {e}")

    return render_template('dashboard/connection.html',
                           user=user,
                           accounts=accounts,
                           active_page='connection')


@dashboard_bp.route('/profile')
@login_required
def profile():
    user = get_user_data(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    verify_token = str(uuid.uuid4())
    bot_username = os.getenv('NOTIF_BOT_USERNAME', 'NamaBotLu_bot')
    bot_link = f"https://t.me/{bot_username}?start={verify_token}"
    is_notif_connected = False

    if supabase:
        try:
            supabase.table('users').update({'verification_token': verify_token}).eq('id', user.id).execute()
        except Exception as e:
            logger.warning(f"Profile: Kolom verification_token tidak ada di DB, fitur bot-link mungkin tidak berfungsi: {e}")
        try:
            raw_user = supabase.table('users').select("notification_chat_id").eq('id', user.id).execute()
            if raw_user.data and raw_user.data[0].get('notification_chat_id'):
                is_notif_connected = True
        except Exception as e:
            logger.warning(f"Profile: Gagal cek notification_chat_id: {e}")

    return render_template('dashboard/profile.html',
                           user=user,
                           active_page='profile',
                           bot_link=bot_link,
                           is_notif_connected=is_notif_connected)


@dashboard_bp.route('/payment')
@login_required
def payment():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    plans_data = FinanceManager.get_plans_structure()
    banks = []
    transactions = []
    has_pending = False

    if not supabase:
        from local_data import get_local_banks
        banks = get_local_banks()
        from local_data import get_local_plans
        transactions = []
    else:
        try:
            banks = supabase.table('admin_banks').select("*").execute().data or []
        except Exception as e:
            logger.error(f"Payment banks fetch error: {e}")
        try:
            trx_res = supabase.table('transactions')\
                .select("*, pricing_variants(duration_days, pricing_plans(display_name))")\
                .eq('user_id', user.id)\
                .order('created_at', desc=True)\
                .execute()
            transactions = trx_res.data if trx_res.data else []
            has_pending = any(t.get('status') == 'pending' for t in transactions)
        except Exception as e:
            logger.error(f"Payment transactions fetch error: {e}")

    return render_template('dashboard/payment.html',
                           user=user,
                           active_page='payment',
                           plans_json=json.dumps(plans_data),
                           banks=banks,
                           transactions=transactions,
                           has_pending=has_pending)


@dashboard_bp.route('/api/payment/checkout', methods=['POST'])
@login_required
def api_checkout():
    user_id = session['user_id']
    variant_id = request.form.get('variant_id')
    method = request.form.get('payment_method')
    proof = request.files.get('proof_file')

    if not variant_id or not method:
        flash('Data pembayaran tidak lengkap.', 'danger')
        return redirect(url_for('dashboard.payment'))

    success, msg = FinanceManager.create_transaction(user_id, variant_id, method, proof)

    if success:
        flash('✅ Invoice berhasil dibuat! Mohon tunggu konfirmasi admin 1x24 jam.', 'success')
    else:
        flash(f'❌ Gagal: {msg}', 'danger')

    return redirect(url_for('dashboard.payment'))


@dashboard_bp.route('/api/payment/cancel/<trx_id>', methods=['POST'])
@login_required
def api_payment_cancel(trx_id):
    user_id = session['user_id']
    if not supabase:
        flash('Fitur ini tidak tersedia dalam mode demo.', 'warning')
        return redirect(url_for('dashboard.payment'))
    try:
        trx = supabase.table('transactions').select("user_id, status").eq('id', trx_id).execute()
        if not trx.data:
            flash('Transaksi tidak ditemukan.', 'danger')
            return redirect(url_for('dashboard.payment'))
        t = trx.data[0]
        if t['user_id'] != user_id:
            flash('Akses ditolak.', 'danger')
            return redirect(url_for('dashboard.payment'))
        if t['status'] != 'pending':
            flash('Hanya transaksi pending yang bisa dibatalkan.', 'warning')
            return redirect(url_for('dashboard.payment'))
        supabase.table('transactions').update({
            'status': 'cancelled',
            'admin_note': f'Dibatalkan oleh user pada {datetime.utcnow().strftime("%d/%m/%Y %H:%M")} UTC'
        }).eq('id', trx_id).execute()
        flash('✅ Pembayaran berhasil dibatalkan.', 'success')
    except Exception as e:
        logger.error(f"Cancel payment error: {e}")
        flash(f'❌ Gagal membatalkan: {e}', 'danger')
    return redirect(url_for('dashboard.payment'))

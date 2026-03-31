import re
import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from decorators import admin_required
from models.finance import FinanceManager, log_bank_mutation
from extensions import supabase

logger = logging.getLogger("BlastPro_Core")

admin_bp = Blueprint('admin', __name__, url_prefix='/super-admin')

USERS_PER_PAGE = 20


def _local_stats():
    return {
        'total_users': 24,
        'active_bots': 18,
        'active_subs': 15,
        'pending_trx': 3,
        'revenue': 12750000,
        'plans': {'agency': 4, 'pro': 11}
    }


def _local_recent_trx():
    base = datetime.utcnow()
    return [
        {
            'id': '001', 'amount': 800000, 'status': 'pending',
            'payment_method': 'transfer_bank',
            'created_at': (base - timedelta(hours=1)).isoformat(),
            'users': {'email': 'budi.santoso@gmail.com'},
            'pricing_variants': {'pricing_plans': {'code_name': 'UMKM Pro'}}
        },
        {
            'id': '002', 'amount': 150000, 'status': 'approved',
            'payment_method': 'transfer_bank',
            'created_at': (base - timedelta(hours=5)).isoformat(),
            'users': {'email': 'siti.rahayu@yahoo.com'},
            'pricing_variants': {'pricing_plans': {'code_name': 'Starter'}}
        },
        {
            'id': '003', 'amount': 1800000, 'status': 'approved',
            'payment_method': 'transfer_bank',
            'created_at': (base - timedelta(days=1)).isoformat(),
            'users': {'email': 'andi.wijaya@gmail.com'},
            'pricing_variants': {'pricing_plans': {'code_name': 'Agency'}}
        },
        {
            'id': '004', 'amount': 350000, 'status': 'pending',
            'payment_method': 'transfer_bank',
            'created_at': (base - timedelta(days=2)).isoformat(),
            'users': {'email': 'dewi.kurnia@gmail.com'},
            'pricing_variants': {'pricing_plans': {'code_name': 'Starter'}}
        },
        {
            'id': '005', 'amount': 800000, 'status': 'approved',
            'payment_method': 'transfer_bank',
            'created_at': (base - timedelta(days=3)).isoformat(),
            'users': {'email': 'reza.pratama@gmail.com'},
            'pricing_variants': {'pricing_plans': {'code_name': 'UMKM Pro'}}
        },
    ]


def _local_users():
    base = datetime.utcnow()

    class FakeTele:
        def __init__(self, phone, active):
            self.phone_number = phone
            self.is_active = active
            self.first_name = 'Demo'

    class FakeUser:
        def __init__(self, uid, email, username, plan, is_admin, is_banned, sub_days, phone=None):
            self.id = uid
            self.email = email
            self.username = username
            self.is_admin = is_admin
            self.is_banned = is_banned
            self.plan_tier = plan
            self.created_at = base - timedelta(days=sub_days + 5)
            self.sub_end = (base + timedelta(days=sub_days)).isoformat() if sub_days > 0 else None
            self.telegram_account = FakeTele(phone, True) if phone else None

    return [
        FakeUser('local-admin', 'admin@blastpro.id', 'superadmin', 'Agency', True, False, 9999, None),
        FakeUser('u-002', 'budi.santoso@gmail.com', 'budi_santoso', 'UMKM Pro', False, False, 75, '+6281234567890'),
        FakeUser('u-003', 'siti.rahayu@yahoo.com', 'siti_rahayu', 'Starter', False, False, 20, '+6289876543210'),
        FakeUser('u-004', 'andi.wijaya@gmail.com', 'andi_wijaya', 'Agency', False, False, 60, '+6281122334455'),
        FakeUser('u-005', 'dewi.kurnia@gmail.com', 'dewi_kurnia', 'Starter', False, False, 5, None),
        FakeUser('u-006', 'reza.pratama@gmail.com', 'reza_pratama', 'UMKM Pro', False, False, 45, '+6285566778899'),
        FakeUser('u-007', 'tono.hartono@gmail.com', 'tono_hartono', 'Starter', False, True, 0, None),
        FakeUser('u-008', 'linda.susanti@gmail.com', 'linda_susanti', 'Agency', False, False, 88, '+6281999888777'),
        FakeUser('u-009', 'joko.widodo@gmail.com', 'joko_widodo', 'UMKM Pro', False, False, 30, '+6282111222333'),
        FakeUser('u-010', 'maya.sari@yahoo.com', 'maya_sari', 'Starter', False, False, 12, None),
    ]


def _local_transactions():
    base = datetime.utcnow()
    return [
        {
            'id': 'trx-001', 'amount': 800000, 'status': 'pending',
            'payment_method': 'transfer_bank',
            'proof_url': None, 'admin_note': None,
            'created_at': (base - timedelta(hours=2)).isoformat(),
            'users': {'email': 'budi.santoso@gmail.com'},
            'pricing_variants': {'price_display': 'Rp 800.000', 'duration_days': 90,
                                 'pricing_plans': {'display_name': 'UMKM Pro'}}
        },
        {
            'id': 'trx-002', 'amount': 350000, 'status': 'pending',
            'payment_method': 'transfer_bank',
            'proof_url': None, 'admin_note': None,
            'created_at': (base - timedelta(hours=6)).isoformat(),
            'users': {'email': 'dewi.kurnia@gmail.com'},
            'pricing_variants': {'price_display': 'Rp 350.000', 'duration_days': 30,
                                 'pricing_plans': {'display_name': 'UMKM Pro'}}
        },
        {
            'id': 'trx-003', 'amount': 150000, 'status': 'approved',
            'payment_method': 'transfer_bank',
            'proof_url': 'https://example.com/proof1.jpg', 'admin_note': 'Sudah diverifikasi.',
            'created_at': (base - timedelta(days=1)).isoformat(),
            'users': {'email': 'siti.rahayu@yahoo.com'},
            'pricing_variants': {'price_display': 'Rp 150.000', 'duration_days': 30,
                                 'pricing_plans': {'display_name': 'Starter'}}
        },
        {
            'id': 'trx-004', 'amount': 1800000, 'status': 'approved',
            'payment_method': 'transfer_bank',
            'proof_url': 'https://example.com/proof2.jpg', 'admin_note': 'Pembayaran diterima.',
            'created_at': (base - timedelta(days=3)).isoformat(),
            'users': {'email': 'andi.wijaya@gmail.com'},
            'pricing_variants': {'price_display': 'Rp 1.800.000', 'duration_days': 90,
                                 'pricing_plans': {'display_name': 'Agency'}}
        },
        {
            'id': 'trx-005', 'amount': 800000, 'status': 'approved',
            'payment_method': 'transfer_bank',
            'proof_url': 'https://example.com/proof3.jpg', 'admin_note': 'OK.',
            'created_at': (base - timedelta(days=5)).isoformat(),
            'users': {'email': 'reza.pratama@gmail.com'},
            'pricing_variants': {'price_display': 'Rp 800.000', 'duration_days': 90,
                                 'pricing_plans': {'display_name': 'UMKM Pro'}}
        },
        {
            'id': 'trx-006', 'amount': 600000, 'status': 'rejected',
            'payment_method': 'transfer_bank',
            'proof_url': None, 'admin_note': 'Bukti transfer tidak jelas.',
            'created_at': (base - timedelta(days=7)).isoformat(),
            'users': {'email': 'tono.hartono@gmail.com'},
            'pricing_variants': {'price_display': 'Rp 600.000', 'duration_days': 180,
                                 'pricing_plans': {'display_name': 'Starter'}}
        },
    ]


def _local_banks():
    return [
        {'id': 1, 'bank_name': 'BCA', 'account_number': '1234567890',
         'account_holder': 'BLASTPRO INDONESIA', 'balance': 5000000, 'is_active': True},
        {'id': 2, 'bank_name': 'MANDIRI', 'account_number': '0987654321',
         'account_holder': 'BLASTPRO INDONESIA', 'balance': 2750000, 'is_active': True},
        {'id': 3, 'bank_name': 'BRI', 'account_number': '1122334455',
         'account_holder': 'BLASTPRO INDONESIA', 'balance': 1000000, 'is_active': False},
    ]


def _local_mutations():
    base = datetime.utcnow()
    return [
        {'id': 1, 'mutation_type': 'INCOME', 'amount': 800000,
         'balance_before': 4200000, 'balance_after': 5000000,
         'description': 'Pembayaran UMKM Pro - budi.santoso@gmail.com',
         'created_at': (base - timedelta(hours=2)).isoformat(),
         'admin_banks': {'bank_name': 'BCA', 'account_number': '1234567890'}},
        {'id': 2, 'mutation_type': 'INCOME', 'amount': 1800000,
         'balance_before': 2400000, 'balance_after': 4200000,
         'description': 'Pembayaran Agency - andi.wijaya@gmail.com',
         'created_at': (base - timedelta(days=1)).isoformat(),
         'admin_banks': {'bank_name': 'BCA', 'account_number': '1234567890'}},
        {'id': 3, 'mutation_type': 'EXPENSE', 'amount': 500000,
         'balance_before': 3250000, 'balance_after': 2750000,
         'description': 'Biaya operasional server',
         'created_at': (base - timedelta(days=2)).isoformat(),
         'admin_banks': {'bank_name': 'MANDIRI', 'account_number': '0987654321'}},
        {'id': 4, 'mutation_type': 'INCOME', 'amount': 150000,
         'balance_before': 3100000, 'balance_after': 3250000,
         'description': 'Pembayaran Starter - siti.rahayu@yahoo.com',
         'created_at': (base - timedelta(days=3)).isoformat(),
         'admin_banks': {'bank_name': 'MANDIRI', 'account_number': '0987654321'}},
        {'id': 5, 'mutation_type': 'TRANSFER_IN', 'amount': 1000000,
         'balance_before': 0, 'balance_after': 1000000,
         'description': 'Dana awal operasional',
         'created_at': (base - timedelta(days=10)).isoformat(),
         'admin_banks': {'bank_name': 'BRI', 'account_number': '1122334455'}},
    ]


def _local_pricing():
    return [
        {
            'id': 1, 'code_name': 'Starter', 'display_name': 'Starter',
            'features': ['1 Akun Telegram', 'Broadcast Unlimited', 'CRM & Target Grup', 'Jadwal Otomatis', 'Template Pesan'],
            'pricing_variants': [
                {'id': 1, 'duration_days': 30, 'price_raw': 150000, 'price_display': 'Rp 150.000', 'price_strike': '250000', 'is_best_value': False},
                {'id': 2, 'duration_days': 90, 'price_raw': 350000, 'price_display': 'Rp 350.000', 'price_strike': '750000', 'is_best_value': True},
                {'id': 3, 'duration_days': 180, 'price_raw': 600000, 'price_display': 'Rp 600.000', 'price_strike': '1500000', 'is_best_value': False},
            ]
        },
        {
            'id': 2, 'code_name': 'UMKM Pro', 'display_name': 'UMKM Pro',
            'features': ['3 Akun Telegram', 'Semua Fitur Starter', 'Auto-Reply Keyword', 'Prioritas Support'],
            'pricing_variants': [
                {'id': 4, 'duration_days': 30, 'price_raw': 350000, 'price_display': 'Rp 350.000', 'price_strike': '500000', 'is_best_value': False},
                {'id': 5, 'duration_days': 90, 'price_raw': 800000, 'price_display': 'Rp 800.000', 'price_strike': '1500000', 'is_best_value': True},
                {'id': 6, 'duration_days': 180, 'price_raw': 1400000, 'price_display': 'Rp 1.400.000', 'price_strike': '3000000', 'is_best_value': False},
            ]
        },
        {
            'id': 3, 'code_name': 'Agency', 'display_name': 'Agency',
            'features': ['10 Akun Telegram', 'Semua Fitur Pro', 'Multi-Account Management', 'Dedicated Support'],
            'pricing_variants': [
                {'id': 7, 'duration_days': 30, 'price_raw': 750000, 'price_display': 'Rp 750.000', 'price_strike': '1200000', 'is_best_value': False},
                {'id': 8, 'duration_days': 90, 'price_raw': 1800000, 'price_display': 'Rp 1.800.000', 'price_strike': '3600000', 'is_best_value': True},
                {'id': 9, 'duration_days': 180, 'price_raw': 3000000, 'price_display': 'Rp 3.000.000', 'price_strike': '7200000', 'is_best_value': False},
            ]
        },
    ]


@admin_bp.route('')
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    if not supabase:
        now_wib = (datetime.utcnow() + timedelta(hours=7)).strftime("%H:%M WIB")
        return render_template('admin/index.html',
                               stats=_local_stats(),
                               recent_trx=_local_recent_trx(),
                               now_wib=now_wib,
                               active_page='dashboard')
    try:
        users_res = supabase.table('users').select("id, is_banned, plan_tier", count='exact').execute()
        bots_res = supabase.table('telegram_accounts').select("id", count='exact').eq('is_active', True).execute()

        users_data = users_res.data
        pending_trx = supabase.table('transactions').select("id", count='exact').eq('status', 'pending').execute().count
        revenue_data = supabase.table('transactions').select("amount").eq('status', 'approved').execute().data
        total_revenue = sum(item['amount'] for item in revenue_data) if revenue_data else 0

        now_iso = datetime.utcnow().isoformat()
        active_subs = supabase.table('users').select("id", count='exact')\
            .neq('plan_tier', 'Starter').gt('subscription_end', now_iso).execute().count

        stats = {
            'total_users': users_res.count or 0,
            'active_bots': bots_res.count or 0,
            'active_subs': active_subs or 0,
            'pending_trx': pending_trx or 0,
            'revenue': total_revenue,
            'plans': {
                'agency': sum(1 for u in users_data if u.get('plan_tier') == 'Agency'),
                'pro': sum(1 for u in users_data if u.get('plan_tier') == 'UMKM Pro')
            }
        }

        recent_trx = supabase.table('transactions')\
            .select("*, users(email), pricing_variants(pricing_plans(code_name))")\
            .order('created_at', desc=True).limit(5).execute().data

        now_wib = (datetime.utcnow() + timedelta(hours=7)).strftime("%H:%M WIB")

        return render_template('admin/index.html',
                               stats=stats,
                               recent_trx=recent_trx,
                               now_wib=now_wib,
                               active_page='dashboard')

    except Exception as e:
        logger.error(f"Admin Dashboard Error: {e}")
        return render_template('admin/index.html',
                               stats={'total_users': 0, 'revenue': 0, 'pending_trx': 0,
                                      'active_subs': 0, 'active_bots': 0, 'plans': {'agency': 0, 'pro': 0}},
                               recent_trx=[],
                               now_wib="Error",
                               active_page='dashboard')


@admin_bp.route('/users')
@admin_required
def users():
    if not supabase:
        search_q = request.args.get('q', '').strip().lower()
        all_users = _local_users()
        if search_q:
            all_users = [u for u in all_users if search_q in u.email.lower() or search_q in u.username.lower()]
        return render_template('admin/users.html',
                               users=all_users,
                               current_page=1,
                               total_pages=1,
                               total_count=len(all_users),
                               search_q=search_q,
                               active_page='users')
    try:
        page = request.args.get('page', 1, type=int)
        search_q = request.args.get('q', '').strip()

        offset = (page - 1) * USERS_PER_PAGE

        query = supabase.table('users').select(
            "id, email, username, is_admin, is_banned, plan_tier, subscription_end, created_at, "
            "telegram_accounts(id, phone_number, is_active, first_name)",
            count='exact'
        ).order('created_at', desc=True)

        if search_q:
            query = query.or_(f"email.ilike.%{search_q}%,username.ilike.%{search_q}%")

        res = query.range(offset, offset + USERS_PER_PAGE - 1).execute()
        raw_users = res.data if res.data else []
        total_count = res.count or 0
        total_pages = max(1, -(-total_count // USERS_PER_PAGE))

        class UserW:
            def __init__(self, d):
                self.id = d['id']
                self.email = d['email']
                self.username = d.get('username', '')
                self.is_admin = d.get('is_admin')
                self.is_banned = d.get('is_banned')
                self.plan_tier = d.get('plan_tier', 'Starter')
                self.sub_end = d.get('subscription_end')
                raw_date = d.get('created_at')
                try:
                    self.created_at = datetime.fromisoformat(raw_date.replace('Z', '+00:00')) if raw_date else datetime.utcnow()
                except Exception:
                    self.created_at = datetime.utcnow()
                self.telegram_account = None
                tele_list = d.get('telegram_accounts', [])
                if tele_list:
                    t = tele_list[0]
                    self.telegram_account = type('o', (object,), t)()

        final_list = [UserW(u) for u in raw_users]

        return render_template('admin/users.html',
                               users=final_list,
                               current_page=page,
                               total_pages=total_pages,
                               total_count=total_count,
                               search_q=search_q,
                               active_page='users')
    except Exception as e:
        logger.error(f"Admin Users Error: {e}")
        flash("Gagal memuat daftar pengguna: Database tidak terhubung.", "warning")
        return render_template('admin/users.html',
                               users=[],
                               current_page=1,
                               total_pages=1,
                               total_count=0,
                               search_q='',
                               active_page='users')


@admin_bp.route('/user/<int:user_id>')
@admin_required
def user_detail(user_id):
    try:
        u_res = supabase.table('users').select("*").eq('id', user_id).execute()
        if not u_res.data:
            flash("Pengguna tidak ditemukan.", "danger")
            return redirect(url_for('admin.users'))
        user = u_res.data[0]
        t_res = supabase.table('telegram_accounts').select("*").eq('user_id', user_id).execute()
        tele = t_res.data[0] if t_res.data else None
        logs_res = supabase.table('blast_logs').select("*").eq('user_id', user_id).order('created_at', desc=True).limit(20).execute()
        logs = logs_res.data if logs_res.data else []
        sched_res = supabase.table('blast_schedules').select("id", count='exact').eq('user_id', user_id).eq('is_active', True).execute()
        active_schedules = sched_res.count or 0
        return render_template('admin/user_detail.html',
                               user=user, tele=tele, logs=logs,
                               active_schedules=active_schedules, active_page='users')
    except Exception as e:
        logger.error(f"User Detail Error: {e}")
        flash(f"Gagal memuat detail pengguna: {e}", "danger")
        return redirect(url_for('admin.users'))


@admin_bp.route('/update-plan/<int:user_id>', methods=['POST'])
@admin_required
def update_plan(user_id):
    plan = request.form.get('plan')
    days = int(request.form.get('days', 30))
    try:
        new_expiry = (datetime.utcnow() + timedelta(days=days)).isoformat()
        supabase.table('users').update({'plan_tier': plan, 'subscription_end': new_expiry}).eq('id', user_id).execute()
        logger.info(f"[ADMIN] User #{user_id} di-upgrade ke {plan} oleh Admin {session.get('user_id')}")
        flash(f"Berhasil update user #{user_id} ke paket {plan} ({days} hari).", 'success')
    except Exception as e:
        flash(f"Gagal update plan: {e}", 'danger')
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/reset-session/<int:user_id>', methods=['POST'])
@admin_required
def reset_session(user_id):
    try:
        supabase.table('telegram_accounts').update({
            'is_active': False,
            'session_string': None
        }).eq('user_id', user_id).execute()
        logger.info(f"[ADMIN] Sesi Telegram User #{user_id} di-reset oleh Admin {session.get('user_id')}")
        flash(f"Sesi Telegram User #{user_id} berhasil di-reset paksa.", 'warning')
    except Exception as e:
        flash(f"Gagal reset sesi: {e}", 'danger')
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/reset-password/<int:user_id>', methods=['POST'])
@admin_required
def reset_password(user_id):
    new_password = request.form.get('new_password')
    if not new_password or len(new_password) < 8:
        flash("❌ Password baru minimal 8 karakter!", "danger")
        return redirect(url_for('admin.user_detail', user_id=user_id))
    try:
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256:260000')
        supabase.table('users').update({'password': hashed_password}).eq('id', user_id).execute()
        logger.info(f"[ADMIN] Password User #{user_id} di-reset oleh Admin {session.get('user_id')}")
        flash(f"✅ Password User #{user_id} berhasil diubah secara paksa!", 'success')
    except Exception as e:
        logger.error(f"Reset Password Error: {e}")
        flash(f"❌ Gagal mereset password: {e}", 'danger')
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/ban/<int:user_id>', methods=['POST'])
@admin_required
def ban_user(user_id):
    try:
        u_data = supabase.table('users').select("is_banned").eq('id', user_id).execute().data
        if not u_data:
            return redirect(url_for('admin.users'))
        new_val = not u_data[0].get('is_banned', False)
        supabase.table('users').update({'is_banned': new_val}).eq('id', user_id).execute()
        action = "di-BAN" if new_val else "di-UNBAN"
        logger.info(f"[ADMIN] User #{user_id} {action} oleh Admin {session.get('user_id')}")
        if new_val:
            supabase.table('telegram_accounts').update({'is_active': False}).eq('user_id', user_id).execute()
        flash(f"Status User #{user_id} berhasil diubah.", 'success')
    except Exception as e:
        flash(f"Gagal update status: {e}", 'danger')
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/pricing', methods=['GET', 'POST'])
@admin_required
def pricing():
    if not supabase:
        if request.method == 'POST':
            flash('Mode demo: perubahan harga tidak disimpan (Supabase belum terhubung).', 'warning')
            return redirect(url_for('admin.pricing'))
        return render_template('admin/pricing.html', plans=_local_pricing(), active_page='pricing')
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'update_plan':
                plan_id = request.form.get('plan_id')
                features_str = request.form.get('features')
                features_list = [f.strip() for f in features_str.split(',') if f.strip()]
                supabase.table('pricing_plans').update({'features': features_list}).eq('id', plan_id).execute()
                flash('Fitur paket berhasil diupdate!', 'success')
            elif action == 'update_variant':
                var_id = request.form.get('id')
                price_raw = request.form.get('price_raw')
                price_strike = request.form.get('price_strike')
                price_disp = request.form.get('price_display')
                is_best_value = request.form.get('is_best_value') == '1'
                clean_raw = re.sub(r'[^\d]', '', str(price_raw)) if price_raw else '0'
                clean_strike = re.sub(r'[^\d]', '', str(price_strike)) if price_strike else '0'
                if is_best_value:
                    v_res = supabase.table('pricing_variants').select("plan_id").eq('id', var_id).execute()
                    if v_res.data:
                        plan_id_for_reset = v_res.data[0]['plan_id']
                        supabase.table('pricing_variants').update({'is_best_value': False}).eq('plan_id', plan_id_for_reset).execute()
                supabase.table('pricing_variants').update({
                    'price_raw': int(clean_raw),
                    'price_strike': str(clean_strike),
                    'price_display': price_disp,
                    'is_best_value': is_best_value
                }).eq('id', var_id).execute()
                flash('Harga & Diskon berhasil diupdate!', 'success')
            elif action == 'add_variant':
                plan_id = request.form.get('plan_id')
                duration_days = int(request.form.get('duration_days', 30))
                price_raw_str = re.sub(r'[^\d]', '', request.form.get('price_raw', '0'))
                price_display = request.form.get('price_display', '')
                supabase.table('pricing_variants').insert({
                    'plan_id': plan_id,
                    'duration_days': duration_days,
                    'price_raw': int(price_raw_str) if price_raw_str else 0,
                    'price_display': price_display,
                    'price_strike': None,
                    'is_best_value': False
                }).execute()
                flash('Variant baru berhasil ditambahkan!', 'success')
            return redirect(url_for('admin.pricing'))

        try:
            plans = supabase.table('pricing_plans').select("*, pricing_variants(*)").order('id').execute().data
        except Exception as db_e:
            logger.error(f"DB Error Pricing: {db_e}")
            flash("Gagal ambil data harga. Cek tabel database.", "danger")
            plans = []

        return render_template('admin/pricing.html', plans=plans, active_page='pricing')
    except Exception as e:
        logger.error(f"Page Error Pricing: {e}")
        flash(f"System Error: {e}", "danger")
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/pricing/delete-variant', methods=['POST'])
@admin_required
def pricing_delete_variant():
    var_id = request.form.get('variant_id')
    if not supabase or not var_id:
        flash('Tidak bisa menghapus dalam mode demo.', 'warning')
        return redirect(url_for('admin.pricing'))
    try:
        trx_count = supabase.table('transactions').select("id", count='exact').eq('plan_variant_id', var_id).execute().count or 0
        if trx_count > 0:
            flash(f'Tidak bisa hapus — variant ini digunakan oleh {trx_count} transaksi.', 'danger')
        else:
            supabase.table('pricing_variants').delete().eq('id', var_id).execute()
            flash('Variant berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Gagal menghapus variant: {e}', 'danger')
    return redirect(url_for('admin.pricing'))


def _build_finance_stats(all_trx_data=None):
    stats = {'pending': 0, 'approved': 0, 'rejected': 0, 'revenue': 0.0}
    if not supabase:
        if all_trx_data:
            for t in all_trx_data:
                s = t.get('status', '')
                if s in stats:
                    stats[s] = stats[s] + 1
                if s == 'approved':
                    stats['revenue'] += float(t.get('amount') or 0)
        return stats
    try:
        all_t = supabase.table('transactions').select("status, amount").execute().data or []
        for t in all_t:
            s = t.get('status', '')
            if s in stats:
                stats[s] += 1
            if s == 'approved':
                stats['revenue'] += float(t.get('amount') or 0)
    except Exception as e:
        logger.error(f"Finance stats error: {e}")
    return stats


@admin_bp.route('/finance')
@admin_required
def finance():
    status = request.args.get('status', 'all')
    if not supabase:
        all_trx = _local_transactions()
        if status != 'all':
            filtered = [t for t in all_trx if t['status'] == status]
        else:
            filtered = all_trx
        stats = _build_finance_stats(all_trx)
        return render_template('admin/finance.html',
                               transactions=filtered,
                               current_filter=status,
                               current_page=1,
                               total_pages=1,
                               total_count=len(filtered),
                               stats=stats,
                               active_page='finance')
    page = request.args.get('page', 1, type=int)
    per_page = 30
    offset = (page - 1) * per_page
    trx = []
    total_count = 0
    try:
        query = supabase.table('transactions').select(
            "*, users(email), pricing_variants(price_display, duration_days, pricing_plans(display_name))",
            count='exact'
        )
        if status != 'all':
            query = query.eq('status', status)
        res = query.order('created_at', desc=True).range(offset, offset + per_page - 1).execute()
        trx = res.data if res.data else []
        total_count = res.count or 0
    except Exception as e:
        logger.error(f"Finance Query Error: {e}")
        flash(f"Gagal memuat transaksi: {str(e)}", "warning")

    total_pages = max(1, -(-total_count // per_page))
    stats = _build_finance_stats()
    return render_template('admin/finance.html',
                           transactions=trx,
                           current_filter=status,
                           current_page=page,
                           total_pages=total_pages,
                           total_count=total_count,
                           stats=stats,
                           active_page='finance')


@admin_bp.route('/finance/approve/<string:trx_id>', methods=['POST'])
@admin_required
def approve_trx(trx_id):
    if not supabase:
        flash('Mode demo: aksi approve tidak tersedia (Supabase belum terhubung).', 'warning')
        return redirect(url_for('admin.finance'))
    admin_note = request.form.get('admin_note', '').strip()
    success, msg = FinanceManager.approve_transaction(str(trx_id), session['user_id'], admin_note)
    if success:
        logger.info(f"[ADMIN] Transaksi {trx_id} disetujui oleh Admin {session.get('user_id')}")
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('admin.finance'))


@admin_bp.route('/finance/reject/<string:trx_id>', methods=['POST'])
@admin_required
def reject_trx(trx_id):
    if not supabase:
        flash('Mode demo: aksi reject tidak tersedia (Supabase belum terhubung).', 'warning')
        return redirect(url_for('admin.finance'))
    reason = request.form.get('reason', '').strip()
    success, msg = FinanceManager.reject_transaction(str(trx_id), session['user_id'], reason)
    if success:
        logger.info(f"[ADMIN] Transaksi {trx_id} ditolak oleh Admin {session.get('user_id')}")
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('admin.finance'))


@admin_bp.route('/banks')
@admin_required
def banks():
    if not supabase:
        banks_data = _local_banks()
        total_balance = sum(float(b.get('balance') or 0) for b in banks_data)
        return render_template('admin/banks.html', banks=banks_data, total_balance=total_balance, active_page='banks')
    try:
        res = supabase.table('admin_banks').select("*").order('id').execute()
        banks_data = res.data if res.data else []
        total_balance = sum(float(b.get('balance') or 0) for b in banks_data)
        return render_template('admin/banks.html', banks=banks_data, total_balance=total_balance, active_page='banks')
    except Exception as e:
        logger.error(f"Error load banks: {e}")
        flash("Gagal memuat data bank: Database tidak terhubung.", "warning")
        return render_template('admin/banks.html', banks=[], total_balance=0, active_page='banks')


@admin_bp.route('/banks/save', methods=['POST'])
@admin_required
def save_bank():
    if not supabase:
        flash('Tidak bisa menyimpan dalam mode demo.', 'warning')
        return redirect(url_for('admin.banks'))
    try:
        bank_id = request.form.get('bank_id')
        bank_name = request.form.get('bank_name', '').strip().upper()
        account_number = request.form.get('account_number', '').strip()
        account_holder = request.form.get('account_holder', '').strip().upper()
        if not bank_name:
            flash('❌ Nama bank tidak boleh kosong.', 'danger')
            return redirect(url_for('admin.banks'))
        data = {
            'bank_name': bank_name,
            'account_number': account_number,
            'account_holder': account_holder
        }
        if bank_id:
            try:
                supabase.table('admin_banks').update(data).eq('id', bank_id).execute()
            except Exception:
                supabase.table('admin_banks').update({'bank_name': bank_name}).eq('id', bank_id).execute()
            flash('✅ Rekening berhasil diupdate.', 'success')
        else:
            data['balance'] = 0
            data['is_active'] = True
            try:
                supabase.table('admin_banks').insert(data).execute()
            except Exception:
                supabase.table('admin_banks').insert({'bank_name': bank_name, 'balance': 0}).execute()
            flash('✅ Rekening baru berhasil ditambahkan.', 'success')
    except Exception as e:
        logger.error(f"Save Bank Error: {e}")
        flash('❌ Gagal menyimpan rekening.', 'danger')
    return redirect(url_for('admin.banks'))


@admin_bp.route('/banks/transfer', methods=['POST'])
@admin_required
def transfer_balance():
    if not supabase:
        flash('Tidak bisa memindahkan dana dalam mode demo.', 'warning')
        return redirect(url_for('admin.banks'))
    try:
        source_id = request.form.get('source_bank_id')
        dest_id = request.form.get('dest_bank_id')
        amount_str = request.form.get('amount')
        desc = request.form.get('description', 'Pindah Dana Internal')
        amount = float(re.sub(r'[^\d]', '', amount_str))

        if source_id == dest_id:
            flash('⚠️ Rekening asal dan tujuan tidak boleh sama!', 'warning')
            return redirect(url_for('admin.banks'))

        src_res = supabase.table('admin_banks').select("bank_name, balance").eq('id', source_id).execute()
        dest_res = supabase.table('admin_banks').select("bank_name, balance").eq('id', dest_id).execute()
        src_balance = float(src_res.data[0].get('balance') or 0)
        dest_balance = float(dest_res.data[0].get('balance') or 0)

        if src_balance < amount:
            flash(f"❌ Saldo {src_res.data[0]['bank_name']} tidak mencukupi!", 'danger')
            return redirect(url_for('admin.banks'))

        new_src = src_balance - amount
        new_dest = dest_balance + amount
        supabase.table('admin_banks').update({'balance': new_src}).eq('id', source_id).execute()
        supabase.table('admin_banks').update({'balance': new_dest}).eq('id', dest_id).execute()
        log_bank_mutation(source_id, 'TRANSFER_OUT', amount, src_balance, new_src, f"Ke: {dest_res.data[0]['bank_name']} | {desc}")
        log_bank_mutation(dest_id, 'TRANSFER_IN', amount, dest_balance, new_dest, f"Dari: {src_res.data[0]['bank_name']} | {desc}")
        flash(f"💸 Mutasi Sukses! Rp {amount:,.0f} dipindah.", 'success')
    except Exception as e:
        flash(f'❌ Gagal memindahkan dana: {e}', 'danger')
    return redirect(url_for('admin.banks'))


@admin_bp.route('/banks/toggle/<int:bank_id>', methods=['POST'])
@admin_required
def toggle_bank(bank_id):
    if not supabase:
        flash('Tidak bisa mengubah status dalam mode demo.', 'warning')
        return redirect(url_for('admin.banks'))
    try:
        b_data = supabase.table('admin_banks').select("*").eq('id', bank_id).execute().data
        if b_data:
            current_val = b_data[0].get('is_active', True)
            new_val = not current_val
            supabase.table('admin_banks').update({'is_active': new_val}).eq('id', bank_id).execute()
            flash('✅ Status rekening diubah.', 'success')
    except Exception as e:
        logger.error(f'Toggle bank status error: {e}')
        flash('❌ Kolom is_active belum ada di database. Perlu migrasi skema.', 'warning')
    return redirect(url_for('admin.banks'))


@admin_bp.route('/banks/delete/<int:bank_id>', methods=['POST'])
@admin_required
def delete_bank(bank_id):
    if not supabase:
        flash('Tidak bisa menghapus dalam mode demo.', 'warning')
        return redirect(url_for('admin.banks'))
    try:
        mut_count = supabase.table('bank_mutations').select("id", count='exact').eq('bank_id', bank_id).execute().count or 0
        if mut_count > 0:
            try:
                supabase.table('admin_banks').update({'is_active': False}).eq('id', bank_id).execute()
                flash(f'Rekening dinonaktifkan (memiliki {mut_count} riwayat mutasi, tidak dihapus permanen).', 'info')
            except Exception:
                flash(f'Rekening ini memiliki {mut_count} riwayat mutasi dan tidak dapat dihapus permanen.', 'warning')
        else:
            supabase.table('admin_banks').delete().eq('id', bank_id).execute()
            flash('✅ Rekening berhasil dihapus.', 'success')
    except Exception as e:
        logger.error(f"Delete Bank Error: {e}")
        flash(f'❌ Gagal menghapus rekening: {e}', 'danger')
    return redirect(url_for('admin.banks'))


@admin_bp.route('/banks/manual_entry', methods=['POST'])
@admin_required
def manual_bank_entry():
    if not supabase:
        flash('Tidak bisa input kas dalam mode demo.', 'warning')
        return redirect(url_for('admin.banks'))
    try:
        bank_id = request.form.get('bank_id')
        entry_type = request.form.get('entry_type')
        amount_str = request.form.get('amount')
        desc = request.form.get('description', 'Manual Entry')
        amount = float(re.sub(r'[^\d]', '', amount_str)) if amount_str else 0

        bank = supabase.table('admin_banks').select("bank_name, balance").eq('id', bank_id).execute().data[0]
        current_balance = float(bank.get('balance') or 0)
        new_balance = current_balance

        if entry_type == 'INCOME':
            new_balance = current_balance + amount
            flash(f'✅ Kas Masuk Rp {amount:,.0f} ke {bank["bank_name"]} berhasil.', 'success')
        elif entry_type == 'EXPENSE':
            new_balance = current_balance - amount
            flash(f'✅ Kas Keluar Rp {amount:,.0f} dari {bank["bank_name"]} berhasil.', 'success')
        elif entry_type == 'ADJUSTMENT':
            new_balance = amount
            amount = abs(new_balance - current_balance)
            flash(f'✅ Saldo {bank["bank_name"]} disesuaikan menjadi Rp {new_balance:,.0f}.', 'success')

        supabase.table('admin_banks').update({'balance': new_balance}).eq('id', bank_id).execute()
        log_bank_mutation(bank_id, entry_type, amount, current_balance, new_balance, desc)

    except Exception as e:
        logger.error(f"Manual Entry Error: {e}")
        flash(f'❌ Gagal memproses data: {e}', 'danger')

    return redirect(url_for('admin.banks'))


@admin_bp.route('/mutations')
@admin_required
def mutations():
    filter_type = request.args.get('type', '')
    filter_bank = request.args.get('bank_id', '')
    filter_date_from = request.args.get('date_from', '')
    filter_date_to = request.args.get('date_to', '')
    page = request.args.get('page', 1, type=int)
    per_page = 50

    if not supabase:
        local_data = _local_mutations()
        total_income = sum(m['amount'] for m in local_data if m['mutation_type'] in ['INCOME', 'TRANSFER_IN'])
        total_expense = sum(m['amount'] for m in local_data if m['mutation_type'] in ['EXPENSE', 'TRANSFER_OUT'])
        return render_template('admin/mutations.html',
                               mutations=local_data,
                               current_page=1,
                               total_pages=1,
                               total_income=total_income,
                               total_expense=total_expense,
                               net=total_income - total_expense,
                               banks=[],
                               filter_type=filter_type,
                               filter_bank=filter_bank,
                               filter_date_from=filter_date_from,
                               filter_date_to=filter_date_to,
                               active_page='mutations')
    try:
        offset = (page - 1) * per_page
        query = supabase.table('bank_mutations').select("*, admin_banks(bank_name)", count='exact').order('created_at', desc=True)
        if filter_type:
            query = query.eq('mutation_type', filter_type)
        if filter_bank:
            query = query.eq('bank_id', filter_bank)
        if filter_date_from:
            query = query.gte('created_at', filter_date_from)
        if filter_date_to:
            query = query.lte('created_at', filter_date_to + 'T23:59:59')

        res = query.range(offset, offset + per_page - 1).execute()
        mutations_data = res.data if res.data else []
        total_count = res.count or 0
        total_pages = max(1, -(-total_count // per_page))

        all_for_stats_q = supabase.table('bank_mutations').select("mutation_type, amount")
        if filter_type:
            all_for_stats_q = all_for_stats_q.eq('mutation_type', filter_type)
        if filter_bank:
            all_for_stats_q = all_for_stats_q.eq('bank_id', filter_bank)
        if filter_date_from:
            all_for_stats_q = all_for_stats_q.gte('created_at', filter_date_from)
        if filter_date_to:
            all_for_stats_q = all_for_stats_q.lte('created_at', filter_date_to + 'T23:59:59')
        all_for_stats = all_for_stats_q.execute().data or []

        total_income = sum(float(m['amount']) for m in all_for_stats if m['mutation_type'] in ['INCOME', 'TRANSFER_IN'])
        total_expense = sum(float(m['amount']) for m in all_for_stats if m['mutation_type'] in ['EXPENSE', 'TRANSFER_OUT'])

        banks_list = supabase.table('admin_banks').select("id, bank_name").execute().data or []

        return render_template('admin/mutations.html',
                               mutations=mutations_data,
                               current_page=page,
                               total_pages=total_pages,
                               total_income=total_income,
                               total_expense=total_expense,
                               net=total_income - total_expense,
                               banks=banks_list,
                               filter_type=filter_type,
                               filter_bank=filter_bank,
                               filter_date_from=filter_date_from,
                               filter_date_to=filter_date_to,
                               active_page='mutations')
    except Exception as e:
        logger.error(f"Error load mutations: {e}")
        flash("Gagal memuat mutasi: Database tidak terhubung.", "warning")
        return render_template('admin/mutations.html',
                               mutations=[],
                               current_page=1,
                               total_pages=1,
                               total_income=0,
                               total_expense=0,
                               net=0,
                               banks=[],
                               filter_type='',
                               filter_bank='',
                               filter_date_from='',
                               filter_date_to='',
                               active_page='mutations')


@admin_bp.route('/mutations/export')
@admin_required
def mutations_export():
    if not supabase:
        flash("Export tidak tersedia dalam mode demo.", "warning")
        return redirect(url_for('admin.mutations'))
    try:
        import csv
        import io
        from flask import Response

        query = supabase.table('bank_mutations').select("*, admin_banks(bank_name)").order('created_at', desc=True)
        filter_type = request.args.get('type', '')
        filter_bank = request.args.get('bank_id', '')
        filter_date_from = request.args.get('date_from', '')
        filter_date_to = request.args.get('date_to', '')
        if filter_type:
            query = query.eq('mutation_type', filter_type)
        if filter_bank:
            query = query.eq('bank_id', filter_bank)
        if filter_date_from:
            query = query.gte('created_at', filter_date_from)
        if filter_date_to:
            query = query.lte('created_at', filter_date_to + 'T23:59:59')

        data = query.execute().data or []
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Tanggal (WIB)', 'Rekening', 'Tipe', 'Nominal (Rp)', 'Saldo Sebelum', 'Saldo Sesudah', 'Keterangan'])
        for m in data:
            try:
                dt = datetime.fromisoformat(m['created_at'].replace('Z', '+00:00'))
                wib = (dt + timedelta(hours=7)).strftime('%d/%m/%Y %H:%M')
            except Exception:
                wib = m.get('created_at', '')[:16]
            writer.writerow([
                wib,
                m['admin_banks']['bank_name'] if m.get('admin_banks') else '—',
                m.get('mutation_type', ''),
                int(m.get('amount', 0)),
                int(m.get('balance_before', 0)),
                int(m.get('balance_after', 0)),
                m.get('description', '')
            ])
        output.seek(0)
        filename = f"mutasi_blastpro_{datetime.now().strftime('%Y%m%d')}.csv"
        return Response(output.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition': f'attachment; filename={filename}'})
    except Exception as e:
        logger.error(f"Export mutations error: {e}")
        flash(f"Gagal export: {e}", "danger")
        return redirect(url_for('admin.mutations'))

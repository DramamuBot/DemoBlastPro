import time
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from extensions import supabase, failed_logins, failed_resets
from utils.security import (
    PasswordVault, AntiSpamGuard, InputSanitizer,
    WeakPasswordError, SpamEmailError, SecurityViolation,
    TokenExpiredError, InvalidTokenError
)
from utils.mailer import mailer
from config import SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASS, DEMO_USER_EMAIL, DEMO_USER_PASS

logger = logging.getLogger("BlastPro_Core")

auth_bp = Blueprint('auth', __name__)


def _get_token_manager():
    from tokens import token_manager
    return token_manager


@auth_bp.route('/')
def index():
    pricing_data = {}
    if supabase:
        try:
            from models.finance import FinanceManager
            pricing_data = FinanceManager.get_plans_structure()
        except Exception as e:
            logger.error(f"Gagal load pricing di Landing Page: {e}")
    if not pricing_data:
        try:
            from local_data import get_local_plans
            pricing_data = get_local_plans()
        except Exception as e:
            logger.error(f"Gagal load local pricing: {e}")
    return render_template('landing/index.html', pricing=pricing_data, now=datetime.now())


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('is_admin'):
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('dashboard.overview'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        now = time.time()
        fl = failed_logins.get(email, {'count': 0, 'blocked_until': 0})
        if fl['blocked_until'] > now:
            sisa = int(fl['blocked_until'] - now)
            flash(f"Terlalu banyak percobaan gagal. Coba lagi dalam {sisa} detik.", "danger")
            return render_template('auth/combined.html', active_form='login')

        if not supabase:
            if email == SUPER_ADMIN_EMAIL.lower() and password == SUPER_ADMIN_PASS:
                failed_logins.pop(email, None)
                session['user_id'] = 'local-admin'
                session['username'] = 'Admin'
                session['is_banned'] = False
                session['is_admin'] = True
                flash("Selamat datang kembali, Admin!", "success")
                return redirect(url_for('admin.dashboard'))
            elif email == DEMO_USER_EMAIL.lower() and password == DEMO_USER_PASS:
                failed_logins.pop(email, None)
                session['user_id'] = 'local-user'
                session['username'] = 'User'
                session['is_banned'] = False
                session['is_admin'] = False
                flash("Selamat datang kembali, User!", "success")
                return redirect(url_for('dashboard.overview'))
            else:
                fl['count'] = fl.get('count', 0) + 1
                if fl['count'] >= 5:
                    fl['blocked_until'] = now + 300
                    fl['count'] = 0
                    flash("Akun sementara diblokir karena 5x percobaan gagal. Coba lagi dalam 5 menit.", "danger")
                else:
                    sisa_coba = 5 - fl['count']
                    flash(f"Email atau password salah. Sisa percobaan: {sisa_coba}x.", "danger")
                failed_logins[email] = fl
        else:
            try:
                res = supabase.table('users').select('*').eq('email', email).execute()
                if res.data:
                    user = res.data[0]
                    if PasswordVault.verify_password(user.get('password'), password):
                        if not user.get('is_verified', False):
                            flash("Akun belum diverifikasi! Cek email Anda.", "warning")
                            return redirect(url_for('auth.login'))
                        if user.get('is_banned', False):
                            flash("Akun Anda telah dinonaktifkan. Hubungi administrator.", "danger")
                            return redirect(url_for('auth.login'))
                        failed_logins.pop(email, None)
                        session['user_id'] = user['id']
                        session['username'] = user['username']
                        session['is_banned'] = bool(user.get('is_banned', False))
                        session['is_admin'] = bool(user.get('is_admin', False))
                        flash(f"Selamat datang kembali, {user['username']}!", "success")
                        if session['is_admin']:
                            return redirect(url_for('admin.dashboard'))
                        return redirect(url_for('dashboard.overview'))
                    else:
                        fl['count'] = fl.get('count', 0) + 1
                        if fl['count'] >= 5:
                            fl['blocked_until'] = now + 300
                            fl['count'] = 0
                            flash("Akun sementara diblokir karena 5x percobaan gagal. Coba lagi dalam 5 menit.", "danger")
                        else:
                            sisa_coba = 5 - fl['count']
                            flash(f"Password salah. Sisa percobaan: {sisa_coba}x.", "danger")
                        failed_logins[email] = fl
                else:
                    flash("Email tidak terdaftar.", "danger")
            except Exception as e:
                logger.error(f"Login Error: {e}")
                flash("Terjadi kesalahan sistem.", "danger")

    post_register = request.args.get('registered') == '1'
    resp = make_response(render_template('auth/combined.html', active_form='login', post_register=post_register))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.overview'))

    saved_username = ""
    saved_email = ""
    ref = request.args.get('ref', '')

    if request.method == 'POST':
        if not supabase:
            flash("Layanan pendaftaran sementara tidak tersedia. Hubungi administrator.", "danger")
            return render_template('auth/combined.html', active_form='register', username='', email='', ref=ref)

        saved_username = request.form.get('username', '')
        saved_email = request.form.get('email', '')
        raw_password = request.form.get('password')

        if not saved_username or not saved_email or not raw_password:
            flash("Semua kolom wajib diisi!", "danger")
            return render_template('auth/combined.html', active_form='register', username=saved_username, email=saved_email, ref=ref)

        username = InputSanitizer.sanitize_username(saved_username)
        email = saved_email.strip().lower()

        try:
            AntiSpamGuard.is_clean_email(email)
            PasswordVault.validate_complexity(raw_password)

            res_email = supabase.table('users').select('id, is_verified').eq('email', email).execute()
            res_uname = supabase.table('users').select('id, is_verified').eq('username', username).execute()
            seen_ids = set()
            combined_data = []
            for row in (res_email.data or []) + (res_uname.data or []):
                if row['id'] not in seen_ids:
                    seen_ids.add(row['id'])
                    combined_data.append(row)
            if combined_data:
                user_check = combined_data[0]
                if user_check.get('is_verified'):
                    flash("Email atau Username sudah terdaftar dan aktif! Silakan langsung Login.", "warning")
                    return redirect(url_for('auth.login'))
                else:
                    supabase.table('users').delete().eq('id', user_check['id']).execute()

            hashed_password = PasswordVault.hash_password(raw_password)
            import datetime as dt_module
            new_user_data = {
                "username": username,
                "email": email,
                "password": hashed_password,
                "is_verified": False,
                "created_at": dt_module.datetime.utcnow().isoformat()
            }
            res = supabase.table('users').insert(new_user_data).execute()

            if res.data:
                tm = _get_token_manager()
                token = tm.generate_verification_token(email)
                verify_url = url_for('auth.verify_email', token=token, _external=True)
                mailer.send_verification_email(to_email=email, user_name=username, verify_url=verify_url)
                flash("Pendaftaran berhasil! Cek kotak masuk atau folder Spam email Anda untuk verifikasi.", "success")
                return redirect(url_for('auth.login', registered='1'))
            else:
                flash("Gagal mendaftar, terjadi gangguan pada database server.", "danger")

        except (SpamEmailError, WeakPasswordError, SecurityViolation) as e:
            flash(str(e), "danger")
            return render_template('auth/combined.html', active_form='register', username=saved_username, email=saved_email, ref=ref)
        except Exception as e:
            logger.error(f"Register Error: {e}")
            flash("Terjadi kesalahan sistem. Coba lagi nanti.", "danger")
            return render_template('auth/combined.html', active_form='register', username=saved_username, email=saved_email, ref=ref)

    resp = make_response(render_template('auth/combined.html', active_form='register', username=saved_username, email=saved_email, ref=ref))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


@auth_bp.route('/verify/<token>')
def verify_email(token):
    try:
        tm = _get_token_manager()
        email = tm.verify_token(token, expiration_seconds=3600)

        user_req = supabase.table('users').select('id, is_verified').eq('email', email).execute()
        if not user_req.data:
            flash("Pengguna tidak ditemukan atau telah dihapus.", "danger")
            return redirect(url_for('auth.register'))

        if user_req.data[0].get('is_verified'):
            flash("Akun Anda sudah terverifikasi sebelumnya. Silakan Login.", "info")
            return redirect(url_for('auth.login'))

        supabase.table('users').update({'is_verified': True}).eq('email', email).execute()
        flash("🔥 Mantap! Email berhasil diverifikasi. Silakan Login ke Dashboard.", "success")
        return redirect(url_for('auth.login'))

    except TokenExpiredError as e:
        flash(str(e), "warning")
    except InvalidTokenError as e:
        flash(str(e), "danger")
    except Exception as e:
        logger.error(f"Verify Route Error: {e}")
        flash("Gagal memverifikasi email. Pastikan link tidak terpotong.", "danger")

    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    from extensions import login_states, broadcast_states
    uid = session.get('user_id')
    uname = session.get('username', 'unknown')
    if uid and uid in login_states:
        try:
            del login_states[uid]
        except Exception:
            pass
    if uid and uid in broadcast_states:
        try:
            broadcast_states[uid] = 'stopped'
        except Exception:
            pass
    session.clear()
    logger.info(f"🚪 User [{uname}] logged out.")
    return redirect(url_for('auth.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        if not supabase:
            flash("Layanan sementara tidak tersedia. Hubungi administrator.", "danger")
            return redirect(url_for('auth.login'))

        ip = request.remote_addr
        now = time.time()
        fr = failed_resets.get(ip, {'count': 0, 'blocked_until': 0})
        if fr['blocked_until'] > now:
            sisa = int((fr['blocked_until'] - now) / 60)
            flash(f"Terlalu banyak permintaan reset. Coba lagi dalam {sisa} menit.", "danger")
            return redirect(url_for('auth.login'))

        email = request.form.get('email', '').strip().lower()
        if not email:
            flash("Email tidak boleh kosong.", "danger")
            return render_template('auth/forgot_password.html')

        try:
            res = supabase.table('users').select('id, username').eq('email', email).execute()
            if res.data:
                user = res.data[0]
                tm = _get_token_manager()
                token = tm.generate_verification_token(email)
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                mailer.send_reset_password_email(email, user['username'], reset_url)

            fr['count'] = fr.get('count', 0) + 1
            if fr['count'] >= 3:
                fr['blocked_until'] = now + 600
                fr['count'] = 0
            failed_resets[ip] = fr

        except Exception as e:
            logger.error(f"Forgot password error: {e}")

        flash("Jika email terdaftar, instruksi reset password telah dikirim ke email Anda.", "info")
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        tm = _get_token_manager()
        email = tm.verify_token(token, expiration_seconds=3600)
    except Exception:
        flash("Link reset password tidak valid atau sudah hangus.", "danger")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_pass = request.form.get('password')
        try:
            PasswordVault.validate_complexity(new_pass)
            hashed_pass = PasswordVault.hash_password(new_pass)
            if not supabase:
                flash("Layanan sementara tidak tersedia.", "danger")
                return render_template('auth/reset_password.html', token=token)
            supabase.table('users').update({'password': hashed_pass}).eq('email', email).execute()
            logger.info(f"Password reset berhasil untuk: {email}")
            flash("✅ Password berhasil diubah! Silakan login.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            logger.error(f"Reset password error: {e}")
            flash(str(e), "danger")

    return render_template('auth/reset_password.html', token=token)

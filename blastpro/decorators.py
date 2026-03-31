import logging
from functools import wraps
from flask import session, redirect, url_for, flash

logger = logging.getLogger("BlastPro_Core")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        session.permanent = True

        # Cek is_banned — langsung dari session agar hemat query
        if session.get('is_banned'):
            flash('⛔ Akun Anda telah diblokir. Hubungi support jika ada pertanyaan.', 'danger')
            return redirect(url_for('auth.logout'))

        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        if session.get('is_admin') is None:
            from models.user import get_user_data
            user = get_user_data(session['user_id'], use_cache=False)
            if not user:
                return redirect(url_for('auth.login'))
            session['is_admin'] = bool(user.is_admin)
            session['is_banned'] = bool(user.is_banned)

        if session.get('is_banned'):
            flash('⛔ Akun Anda telah diblokir.', 'danger')
            return redirect(url_for('auth.logout'))

        if not session.get('is_admin'):
            logger.warning(f"⛔ Akses Admin ditolak untuk UserID {session.get('user_id')} | IP: {_get_request_ip()}")
            flash('⛔ Security Alert: Akses Ditolak. Area ini dipantau.', 'danger')
            return redirect(url_for('dashboard.overview'))

        return f(*args, **kwargs)
    return decorated_function


def _get_request_ip():
    try:
        from flask import request
        return request.remote_addr or 'unknown'
    except Exception:
        return 'unknown'

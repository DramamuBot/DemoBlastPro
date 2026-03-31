import logging
import time
from datetime import datetime
from flask import Blueprint, jsonify, request, session, redirect, url_for, flash
from extensions import supabase
from config import CSRF_EXEMPT_PREFIXES, IS_PRODUCTION
from utils.security import generate_csrf_token, verify_csrf_token

logger = logging.getLogger("BlastPro_Core")

misc_bp = Blueprint('misc', __name__)


def _login_required_api():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    return None


@misc_bp.route('/api/notifications')
def api_get_notifications():
    if 'user_id' not in session:
        return jsonify({'status': 'ok', 'notifications': [], 'unread': 0})
    if not supabase:
        return jsonify({'status': 'error', 'message': 'DB offline'}), 503
    try:
        user_id = str(session['user_id'])
        data = supabase.table('notifications')\
            .select('id,title,message,type,is_read,created_at')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(30)\
            .execute()
        unread = sum(1 for n in data.data if not n['is_read'])
        return jsonify({'status': 'ok', 'notifications': data.data, 'unread': unread})
    except Exception as e:
        logger.error(f"API notif error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@misc_bp.route('/api/notifications/mark-all-read', methods=['POST'])
def api_mark_all_read():
    err = _login_required_api()
    if err:
        return err
    if not supabase:
        return jsonify({'status': 'error'}), 503
    try:
        user_id = str(session['user_id'])
        supabase.table('notifications')\
            .update({'is_read': True})\
            .eq('user_id', user_id)\
            .eq('is_read', False)\
            .execute()
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Mark-all-read error: {e}")
        return jsonify({'status': 'error'}), 500


@misc_bp.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
def api_mark_one_read(notif_id):
    err = _login_required_api()
    if err:
        return err
    if not supabase:
        return jsonify({'status': 'error'}), 503
    try:
        user_id = str(session['user_id'])
        supabase.table('notifications')\
            .update({'is_read': True})\
            .eq('id', notif_id)\
            .eq('user_id', user_id)\
            .execute()
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Notif mark-one-read error: {e}")
        return jsonify({'status': 'error'}), 500

_app_start_time = time.time()


@misc_bp.route('/ping')
def ping():
    uptime_seconds = int(time.time() - _app_start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60

    db_ok = supabase is not None

    from services.auto_reply_service import AutoReplyService
    satpam_active = len(AutoReplyService._clients) > 0 if hasattr(AutoReplyService, '_clients') else False

    return jsonify({
        'status': 'ok',
        'service': 'BlastPro SaaS',
        'version': '2.0',
        'db_connected': db_ok,
        'auto_reply_active': satpam_active,
        'uptime': f"{hours}j {minutes}m",
        'timestamp': datetime.utcnow().isoformat()
    }), 200


def register_app_hooks(app):
    @app.errorhandler(404)
    def handle_404(e):
        if 'user_id' in session:
            return redirect(url_for('dashboard.overview'))
        return redirect(url_for('auth.index'))

    @app.errorhandler(500)
    def handle_500(e):
        logger.error(f"⚠️ Internal Server Error: {e}")
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
        if 'user_id' in session:
            flash('Terjadi kesalahan sistem. Tim kami sedang menangani. Coba lagi sebentar.', 'danger')
            return redirect(url_for('dashboard.overview'))
        return redirect(url_for('auth.index'))

    @app.errorhandler(403)
    def handle_403(e):
        if 'user_id' in session:
            flash('⛔ Akses ditolak. Anda tidak punya izin untuk halaman itu.', 'danger')
            return redirect(url_for('dashboard.overview'))
        return redirect(url_for('auth.login'))

    @app.errorhandler(413)
    def handle_413(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'status': 'error', 'message': 'File terlalu besar. Maksimal 10MB.'}), 413
        flash('❌ File yang diunggah terlalu besar. Batas maksimal adalah 10MB.', 'danger')
        return redirect(request.referrer or url_for('dashboard.overview'))

    @app.before_request
    def csrf_protect_global():
        if 'csrf_token' not in session:
            session['csrf_token'] = generate_csrf_token()
        if request.method == 'POST':
            path = request.path
            if not any(path.startswith(prefix) for prefix in CSRF_EXEMPT_PREFIXES):
                form_token = request.form.get('csrf_token', '')
                session_token = session.get('csrf_token', '')
                if not verify_csrf_token(form_token, session_token):
                    logger.warning(f"⛔ CSRF Attack Detected! Path: {path} | IP: {request.remote_addr}")
                    flash('⛔ Permintaan tidak valid (CSRF). Silakan coba lagi.', 'danger')
                    return redirect(request.referrer or url_for('auth.index'))

    @app.context_processor
    def inject_csrf_token():
        return {'csrf_token': session.get('csrf_token', '')}

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        if IS_PRODUCTION:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

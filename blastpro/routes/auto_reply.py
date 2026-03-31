import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from decorators import login_required
from models.user import get_dashboard_context
from models.auto_reply import AutoReplyManager
from extensions import supabase

logger = logging.getLogger("BlastPro_Core")

auto_reply_bp = Blueprint('auto_reply', __name__)


@auto_reply_bp.route('/dashboard/auto-reply', methods=['GET', 'POST'])
@login_required
def dashboard_auto_reply():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    active_tab = request.args.get('tab', 'all')

    if request.method == 'POST':
        try:
            target = request.form.get('target_phone')

            if 'is_active' in request.form:
                is_active = request.form.get('is_active') == 'on'
            else:
                existing = AutoReplyManager.get_settings(user.id, target)
                is_active = existing.get('is_active', False) if existing else False

            hours = int(request.form.get('cooldown_hours', 0))
            minutes = int(request.form.get('cooldown_minutes', 0))
            total_minutes = (hours * 60) + minutes
            if total_minutes < 1:
                total_minutes = 1

            data = {
                'is_active': is_active,
                'target_phone': target,
                'cooldown_minutes': total_minutes,
                'welcome_message': request.form.get('welcome_message'),
                'updated_at': datetime.utcnow().isoformat()
            }

            AutoReplyManager.update_settings(user.id, data)
            flash('Pengaturan berhasil disimpan!', 'success')
            return redirect(url_for('auto_reply.dashboard_auto_reply', tab=target))

        except Exception as e:
            logger.error(f"Save Error: {e}")
            flash(f"Gagal: {e}", 'danger')

    accounts = []
    if not supabase:
        from local_data import get_local_accounts
        accounts = get_local_accounts()
    else:
        try:
            res = supabase.table('telegram_accounts').select("*").eq('user_id', user.id).eq('is_active', True).execute()
            accounts = res.data or []
        except Exception as e:
            logger.error(f'Auto-reply accounts fetch error: {e}')

    all_keywords = AutoReplyManager.get_keywords(user.id)
    grouped = {'all': []}

    for acc in accounts:
        grouped[acc['phone_number']] = []

    for k in all_keywords:
        raw_target = k.get('target_phone', 'all')
        matched_key = 'all'
        if raw_target != 'all':
            norm_target = AutoReplyManager.normalize_phone(raw_target)
            for acc_phone in grouped.keys():
                if AutoReplyManager.normalize_phone(acc_phone) == norm_target:
                    matched_key = acc_phone
                    break

        if matched_key not in grouped:
            grouped[matched_key] = []
        grouped[matched_key].append(k)

    active_phones_normalized = []
    if not supabase:
        active_phones_normalized = ['all']
    else:
        try:
            active_settings = supabase.table('auto_reply_settings').select("target_phone").eq('user_id', user.id).eq('is_active', True).execute()
            if active_settings.data:
                for s in active_settings.data:
                    active_phones_normalized.append(AutoReplyManager.normalize_phone(s['target_phone']))
        except Exception as e:
            logger.error(f"Active settings fetch error: {e}")

    settings_map = {}
    if not supabase:
        from local_data import get_local_auto_reply_settings
        local_settings = get_local_auto_reply_settings()
        for acc in accounts:
            settings_map[acc['phone_number']] = local_settings
    else:
        try:
            for acc in accounts:
                phone = acc['phone_number']
                normalized = AutoReplyManager.normalize_phone(phone)
                acc_setting = supabase.table('auto_reply_settings').select("*")\
                    .eq('user_id', user.id).eq('target_phone', normalized).execute()
                if acc_setting.data:
                    settings_map[phone] = acc_setting.data[0]
                else:
                    global_setting = supabase.table('auto_reply_settings').select("*")\
                        .eq('user_id', user.id).eq('target_phone', 'all').execute()
                    settings_map[phone] = global_setting.data[0] if global_setting.data else {}
        except Exception as e:
            logger.error(f"Settings Map Error: {e}")

    current_settings = None
    if active_tab == 'all':
        current_settings = AutoReplyManager.get_settings(user.id, 'all')
    elif active_tab in settings_map:
        current_settings = settings_map[active_tab]
    else:
        current_settings = AutoReplyManager.get_settings(user.id, active_tab)

    return render_template('dashboard/auto_reply.html',
                           user=user,
                           accounts=accounts,
                           grouped_keywords=grouped,
                           settings_map=settings_map,
                           active_phones_normalized=active_phones_normalized,
                           active_tab=active_tab,
                           settings=current_settings,
                           active_page='autoreply')


@auto_reply_bp.route('/api/autoreply/toggle', methods=['POST'])
@login_required
def toggle_auto_reply():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return jsonify({'status': 'error', 'message': 'Sesi habis'}), 401

    data = request.json
    phone = data.get('phone')
    is_active = data.get('is_active', False)

    normalized = AutoReplyManager.normalize_phone(phone)
    update_data = {
        'is_active': is_active,
        'target_phone': normalized,
        'updated_at': datetime.utcnow().isoformat()
    }
    try:
        AutoReplyManager.update_settings(user.id, update_data)
        return jsonify({'status': 'success', 'message': 'Status auto-reply berhasil diperbarui'})
    except Exception as e:
        logger.error(f"Toggle Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


@auto_reply_bp.route('/add_keyword', methods=['POST'])
@login_required
def add_keyword():
    user_id = session['user_id']
    keyword = request.form.get('keyword', '').strip()
    response = request.form.get('response', '').strip()
    target = request.form.get('target_phone', 'all')

    if not keyword or not response:
        flash('Keyword dan Balasan wajib diisi.', 'danger')
        return redirect(url_for('auto_reply.dashboard_auto_reply'))

    AutoReplyManager.add_keyword(user_id, keyword, response, target)
    flash('Keyword berhasil ditambahkan!', 'success')
    return redirect(url_for('auto_reply.dashboard_auto_reply', tab=target))


@auto_reply_bp.route('/delete_keyword/<int:id>')
@login_required
def delete_keyword(id):
    AutoReplyManager.delete_keyword(id, session['user_id'])
    flash('Keyword dihapus.', 'success')
    tab = request.args.get('tab', 'all')
    return redirect(url_for('auto_reply.dashboard_auto_reply', tab=tab))


@auto_reply_bp.route('/edit_keyword', methods=['POST'])
@login_required
def edit_keyword():
    user_id = session['user_id']
    k_id = request.form.get('id')
    keyword = request.form.get('keyword', '').strip()
    response = request.form.get('response', '').strip()

    if not k_id or not keyword or not response:
        flash('Data tidak lengkap.', 'danger')
        return redirect(url_for('auto_reply.dashboard_auto_reply'))

    if not supabase:
        flash('Database tidak terhubung. Fitur ini memerlukan koneksi Supabase.', 'danger')
        return redirect(url_for('auto_reply.dashboard_auto_reply'))

    tab = request.form.get('target_phone', 'all')
    try:
        supabase.table('keyword_rules').update({
            'keyword': keyword.lower(),
            'response': response,
        }).eq('id', k_id).eq('user_id', user_id).execute()
        flash('Keyword berhasil diperbarui!', 'success')
    except Exception as e:
        logger.error(f"Edit keyword error: {e}")
        flash('Gagal memperbarui keyword.', 'danger')

    return redirect(url_for('auto_reply.dashboard_auto_reply', tab=tab))

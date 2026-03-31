import logging
import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from decorators import login_required
from models.user import get_dashboard_context
from extensions import supabase

logger = logging.getLogger("BlastPro_Core")

targets_bp = Blueprint('targets', __name__)


@targets_bp.route('/dashboard/targets')
@login_required
def dashboard_targets():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    grouped_targets = {}
    accounts = []

    if not supabase:
        from local_data import get_local_grouped_targets, get_local_accounts
        grouped_targets = get_local_grouped_targets()
        accounts = get_local_accounts()
    else:
        try:
            acc_res = supabase.table('telegram_accounts').select("*").eq('user_id', user.id).eq('is_active', True).execute()
            accounts = acc_res.data if acc_res.data else []

            all_targets = supabase.table('blast_targets').select("*").eq('user_id', user.id).order('created_at', desc=True).execute().data

            for t in all_targets:
                src = t.get('source_phone') or 'Unknown Account'
                tmpl = t.get('template_name') or 'Tanpa Nama'
                if src not in grouped_targets:
                    grouped_targets[src] = {}
                if tmpl not in grouped_targets[src]:
                    grouped_targets[src][tmpl] = []
                grouped_targets[src][tmpl].append(t)

        except Exception as e:
            logger.error(f"Targets Page Error: {e}")

    return render_template('dashboard/targets.html',
                           user=user,
                           grouped_targets=grouped_targets,
                           accounts=accounts,
                           active_page='targets')


@targets_bp.route('/api/target/rename_template', methods=['POST'])
@login_required
def rename_target_template():
    user_id = session['user_id']
    data = request.json
    old_name = data.get('old_name')
    new_name = data.get('new_name')
    source_phone = data.get('source_phone')

    if not old_name or not new_name or not source_phone:
        return jsonify({'status': 'error', 'message': 'Data tidak lengkap'})

    try:
        supabase.table('blast_targets').update({'template_name': new_name})\
            .eq('user_id', user_id)\
            .eq('source_phone', source_phone)\
            .eq('template_name', old_name)\
            .execute()
        return jsonify({'status': 'success', 'message': 'Template berhasil diubah!'})
    except Exception as e:
        logger.error(f"Rename Template Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


@targets_bp.route('/api/target/update_group', methods=['POST'])
@login_required
def update_target_group():
    user_id = session['user_id']
    data = request.json
    target_id = data.get('id')
    new_name = data.get('group_name')
    new_topics = data.get('topic_ids')

    try:
        update_payload = {'group_name': new_name, 'topic_ids': new_topics}
        supabase.table('blast_targets').update(update_payload)\
            .eq('id', target_id)\
            .eq('user_id', user_id)\
            .execute()
        return jsonify({'status': 'success', 'message': 'Data grup berhasil diperbarui.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@targets_bp.route('/api/target/delete_template', methods=['POST'])
@login_required
def delete_target_template():
    user_id = session['user_id']
    data = request.json
    template_name = data.get('template_name')
    source_phone = data.get('source_phone')

    try:
        supabase.table('blast_targets').delete()\
            .eq('user_id', user_id)\
            .eq('source_phone', source_phone)\
            .eq('template_name', template_name)\
            .execute()
        return jsonify({'status': 'success', 'message': 'Koleksi berhasil dihapus.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@targets_bp.route('/delete_target/<int:id>')
@login_required
def delete_target(id):
    try:
        supabase.table('blast_targets').delete().eq('id', id).eq('user_id', session['user_id']).execute()
        flash('Target grup dihapus.', 'success')
    except Exception as e:
        logger.error(f'Delete target error: {e}')
        flash('Gagal menghapus target.', 'danger')
    return redirect(url_for('targets.dashboard_targets'))


@targets_bp.route('/import_targets_csv', methods=['POST'])
@login_required
def import_targets_csv():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    csv_file = request.files.get('csv_file')
    template_name = request.form.get('template_name', f'Import {datetime.now().strftime("%d/%m")}')

    if not csv_file or not csv_file.filename.endswith('.csv'):
        flash('File harus berformat .csv!', 'danger')
        return redirect(url_for('targets.dashboard_targets'))

    try:
        stream = io.StringIO(csv_file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)

        rows = []
        for row in reader:
            try:
                row_data = {k.strip(): v.strip() for k, v in row.items()}
                group_id = int(row_data.get('group_id', '').replace('-100', '').strip())
                group_name = row_data.get('group_name', 'Unknown').strip()
                topic_ids = row_data.get('topic_ids', None)
                rows.append({
                    'user_id': user.id,
                    'group_id': str(group_id),
                    'group_name': group_name,
                    'topic_ids': topic_ids if topic_ids else None,
                    'template_name': template_name,
                    'created_at': datetime.now().isoformat()
                })
            except (ValueError, KeyError) as _row_e:
                logger.warning(f"CSV Row Skip: {_row_e}")
                continue

        if not rows:
            flash('File CSV tidak valid atau data kosong.', 'danger')
            return redirect(url_for('targets.dashboard_targets'))

        supabase.table('blast_targets').insert(rows).execute()
        flash(f'✅ Berhasil import {len(rows)} grup ke koleksi "{template_name}".', 'success')

    except Exception as e:
        logger.error(f"CSV Import Error: {e}")
        flash(f'Gagal import: {str(e)}', 'danger')

    return redirect(url_for('targets.dashboard_targets'))

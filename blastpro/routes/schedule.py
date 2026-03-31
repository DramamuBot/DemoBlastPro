import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from decorators import login_required
from models.user import get_dashboard_context
from models.template import MessageTemplateManager
from extensions import supabase

logger = logging.getLogger("BlastPro_Core")

schedule_bp = Blueprint('schedule', __name__)


@schedule_bp.route('/dashboard/schedule')
@login_required
def dashboard_schedule():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    schedules = []
    templates = []
    targets = []
    accounts = []

    if not supabase:
        from local_data import get_local_schedules, get_local_targets, get_local_accounts
        schedules = get_local_schedules()
        templates = MessageTemplateManager.get_templates(user.id)
        targets = get_local_targets()
        accounts = [{'phone_number': a['phone_number']} for a in get_local_accounts()]
    else:
        try:
            schedules = supabase.table('blast_schedules').select("*").eq('user_id', user.id).order('run_hour', desc=False).execute().data
            templates = MessageTemplateManager.get_templates(user.id)
            targets = supabase.table('blast_targets').select("*").eq('user_id', user.id).execute().data
            acc_res = supabase.table('telegram_accounts').select("phone_number").eq('user_id', user.id).eq('is_active', True).execute()
            accounts = acc_res.data if acc_res.data else []

            for s in schedules:
                t_id = s.get('template_id')
                s['template_name'] = 'Custom / No Template'
                if t_id:
                    found = next((t for t in templates if t['id'] == t_id), None)
                    if found:
                        s['template_name'] = found['name']

        except Exception as e:
            logger.error(f"Schedule Page Error: {e}")

    return render_template('dashboard/schedule.html',
                           user=user,
                           schedules=schedules,
                           templates=templates,
                           targets=targets,
                           accounts=accounts,
                           active_page='schedule')


@schedule_bp.route('/add_schedule', methods=['POST'])
@login_required
def add_schedule():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    hour = request.form.get('hour')
    minute = request.form.get('minute')
    template_id = request.form.get('template_id')
    target_template_name = request.form.get('target_template_name') or None
    sender_phone = request.form.get('sender_phone')

    if not sender_phone or sender_phone == 'auto':
        sender_phone = 'auto'

    try:
        hour_int = int(hour) if hour else -1
        minute_int = int(minute) if minute else -1

        if not (0 <= hour_int <= 23):
            flash('❌ Format jam tidak valid. Jam harus antara 00–23.', 'danger')
            return redirect(url_for('schedule.dashboard_schedule'))
        if not (0 <= minute_int <= 59):
            flash('❌ Format menit tidak valid. Menit harus antara 00–59.', 'danger')
            return redirect(url_for('schedule.dashboard_schedule'))

        data = {
            'user_id': user.id,
            'run_hour': hour_int,
            'run_minute': minute_int,
            'template_id': int(template_id) if template_id else None,
            'sender_phone': sender_phone,
            'is_active': True,
            'target_group_id': None,
            'target_template_name': target_template_name if target_template_name else None
        }

        if target_template_name and supabase:
            try:
                check = supabase.table('blast_targets').select("id").eq('template_name', target_template_name).eq('user_id', user.id).limit(1).execute()
                if not check.data:
                    flash(f'⚠️ Folder "{target_template_name}" kosong atau tidak ditemukan.', 'warning')
                    return redirect(url_for('schedule.dashboard_schedule'))
            except Exception:
                pass

        supabase.table('blast_schedules').insert(data).execute()
        flash('✅ Jadwal berhasil disimpan dan target terkunci!', 'success')

    except Exception as e:
        logger.error(f"Error add schedule: {e}")
        flash(f'❌ Gagal membuat jadwal: {str(e)}', 'danger')

    return redirect(url_for('schedule.dashboard_schedule'))


@schedule_bp.route('/delete_schedule/<int:id>')
@login_required
def delete_schedule(id):
    try:
        supabase.table('blast_schedules').delete().eq('id', id).eq('user_id', session['user_id']).execute()
        flash('Jadwal dihapus.', 'success')
    except Exception as e:
        logger.error(f'Delete schedule error: {e}')
        flash('Gagal menghapus jadwal.', 'danger')
    return redirect(url_for('schedule.dashboard_schedule'))


@schedule_bp.route('/edit_schedule', methods=['POST'])
@login_required
def edit_schedule():
    try:
        schedule_id = request.form.get('schedule_id')
        raw_hour = request.form.get('run_hour')
        raw_minute = request.form.get('run_minute')
        run_hour = int(raw_hour) if raw_hour else -1
        run_minute = int(raw_minute) if raw_minute else -1

        if not (0 <= run_hour <= 23):
            flash('❌ Format jam tidak valid. Jam harus antara 00–23.', 'danger')
            return redirect(url_for('schedule.dashboard_schedule'))
        if not (0 <= run_minute <= 59):
            flash('❌ Format menit tidak valid. Menit harus antara 00–59.', 'danger')
            return redirect(url_for('schedule.dashboard_schedule'))

        sender_phone = request.form.get('sender_phone')
        target_val = request.form.get('target_audience')
        template_id = request.form.get('template_id')

        target_template_name = None
        target_group_id = None

        if target_val and target_val.startswith('folder_'):
            target_template_name = target_val.replace('folder_', '')
        elif target_val and target_val.startswith('TEMPLATE:'):
            target_template_name = target_val.replace('TEMPLATE:', '')
        elif target_val and target_val.startswith('group_'):
            target_group_id = int(target_val.replace('group_', ''))
        elif target_val and target_val.strip().isdigit():
            target_group_id = int(target_val)

        update_data = {
            'run_hour': run_hour,
            'run_minute': run_minute,
            'sender_phone': sender_phone,
            'template_id': int(template_id) if template_id else None,
            'target_template_name': target_template_name,
            'target_group_id': target_group_id
        }

        if schedule_id:
            supabase.table('blast_schedules').update(update_data).eq('id', schedule_id).eq('user_id', session['user_id']).execute()
            flash('Jadwal berhasil diperbarui!', 'success')
        else:
            flash('ID Jadwal tidak ditemukan.', 'danger')

    except Exception as e:
        logger.error(f"Error edit schedule: {e}")
        flash('Gagal memperbarui jadwal.', 'danger')

    return redirect(url_for('schedule.dashboard_schedule'))



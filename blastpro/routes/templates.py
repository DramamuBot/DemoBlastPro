import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from decorators import login_required
from models.user import get_dashboard_context
from models.template import MessageTemplateManager
from extensions import supabase

logger = logging.getLogger("BlastPro_Core")

templates_bp = Blueprint('templates', __name__)


@templates_bp.route('/dashboard/templates')
@login_required
def dashboard_templates():
    user = get_dashboard_context(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    templates = MessageTemplateManager.get_templates(user.id)

    return render_template('dashboard/templates.html',
                           user=user,
                           templates=templates,
                           active_page='templates')


@templates_bp.route('/save_template', methods=['POST'])
@login_required
def save_template():
    user_id = session['user_id']
    name = request.form.get('name', '').strip()
    msg = request.form.get('message', '').strip()
    src_chat = request.form.get('source_chat_id')
    src_msg = request.form.get('source_message_id')

    final_chat = int(src_chat) if src_chat and src_chat != 'null' else None
    final_msg = int(src_msg) if src_msg and src_msg != 'null' else None

    if not name:
        flash('Nama Template wajib diisi.', 'warning')
        return redirect(url_for('templates.dashboard_templates'))

    if MessageTemplateManager.create_template(user_id, name, msg, final_chat, final_msg):
        flash('Template tersimpan (Mode Cloud Reference)!', 'success')
    else:
        flash('Gagal simpan.', 'danger')

    return redirect(url_for('templates.dashboard_templates'))


@templates_bp.route('/delete_template/<int:id>')
@login_required
def delete_template(id):
    success, msg = MessageTemplateManager.delete_template(session['user_id'], id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('templates.dashboard_templates'))


@templates_bp.route('/update_template', methods=['POST'])
@login_required
def update_template():
    user_id = session['user_id']
    t_id = request.form.get('id')
    name = request.form.get('name', '').strip()
    msg = request.form.get('message', '').strip()

    src_chat = request.form.get('source_chat_id')
    src_msg = request.form.get('source_message_id')
    final_chat = int(src_chat) if src_chat and src_chat not in ('null', '') else None
    final_msg = int(src_msg) if src_msg and src_msg not in ('null', '') else None

    if not t_id:
        flash('ID Template tidak valid.', 'danger')
        return redirect(url_for('templates.dashboard_templates'))

    if not name:
        flash('Nama Template wajib diisi.', 'warning')
        return redirect(url_for('templates.dashboard_templates'))

    try:
        data = {
            'name': name,
            'message_text': msg,
            'source_chat_id': final_chat,
            'source_message_id': final_msg,
            'updated_at': datetime.utcnow().isoformat()
        }
        supabase.table('message_templates').update(data).eq('id', t_id).eq('user_id', user_id).execute()
        flash('Template berhasil diperbarui!', 'success')
    except Exception as e:
        flash(f'Gagal update: {str(e)}', 'danger')
        logger.error(f"Template Update Error: {e}")

    return redirect(url_for('templates.dashboard_templates'))

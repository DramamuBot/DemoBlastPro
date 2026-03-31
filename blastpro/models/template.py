import logging
from datetime import datetime
from extensions import supabase

logger = logging.getLogger("BlastPro_Core")


class MessageTemplateManager:

    @staticmethod
    def get_templates(user_id):
        if not supabase:
            from local_data import get_local_templates
            return get_local_templates()
        try:
            res = supabase.table('message_templates').select("*").eq('user_id', user_id).order('created_at', desc=True).execute()
            return res.data if res.data else []
        except Exception as e:
            logger.error(f"Template Fetch Error: {e}")
            return []

    @staticmethod
    def get_template_by_id(template_id):
        if not supabase or not template_id:
            return None
        try:
            res = supabase.table('message_templates').select("*").eq('id', template_id).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Single Template Fetch Error: {e}")
            return None

    @staticmethod
    def create_template(user_id, name, content, source_chat_id=None, source_message_id=None):
        if not supabase:
            return False
        try:
            data = {
                'user_id': user_id,
                'name': name,
                'message_text': content,
                'source_chat_id': source_chat_id,
                'source_message_id': source_message_id,
                'created_at': datetime.utcnow().isoformat()
            }
            supabase.table('message_templates').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Template Create Error: {e}")
            return False

    @staticmethod
    def delete_template(user_id, template_id):
        if not supabase:
            return False, "❌ Database Terputus (Disconnected)"
        try:
            try:
                t_id = int(template_id)
            except ValueError:
                return False, "❌ ID Template tidak valid."

            try:
                usage_check = supabase.table('blast_schedules')\
                    .select("run_hour, run_minute")\
                    .eq('template_id', t_id)\
                    .eq('is_active', True)\
                    .execute()
                if usage_check.data and len(usage_check.data) > 0:
                    times = [f"{s['run_hour']:02d}:{s['run_minute']:02d}" for s in usage_check.data]
                    time_str = ", ".join(times)
                    return False, f"⚠️ Gagal Hapus! Template ini sedang AKTIF digunakan pada Jadwal Pukul: {time_str} WIB. Harap hapus atau ganti jadwalnya terlebih dahulu."
            except Exception as e:
                logger.warning(f"Usage Check Warning: {e}")

            res = supabase.table('message_templates').delete()\
                .eq('id', t_id)\
                .eq('user_id', user_id)\
                .execute()

            if res.data and len(res.data) > 0:
                return True, "✅ Template berhasil dihapus permanen."
            else:
                return False, "❌ Template tidak ditemukan atau sudah dihapus."

        except Exception as e:
            err_msg = str(e).lower()
            logger.error(f"Template Delete Error: {e}")
            if "foreign key" in err_msg or "constraint" in err_msg:
                return False, "🔒 Tidak bisa dihapus: Template ini terkunci karena masih terhubung dengan riwayat broadcast atau jadwal."
            return False, f"⚠️ System Error: {str(e)}"

    @staticmethod
    def update_template(user_id, template_id, name, message_text, source_chat_id=None, source_message_id=None):
        if not supabase:
            return False
        try:
            data = {
                'name': name,
                'message_text': message_text,
                'source_chat_id': source_chat_id,
                'source_message_id': source_message_id,
                'updated_at': datetime.utcnow().isoformat()
            }
            supabase.table('message_templates').update(data).eq('id', template_id).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Template Update Error: {e}")
            return False

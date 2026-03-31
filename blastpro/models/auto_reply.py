import logging
from extensions import supabase

logger = logging.getLogger("BlastPro_Core")


class AutoReplyManager:

    @staticmethod
    def normalize_phone(phone):
        if not phone:
            return 'all'
        if phone == 'all':
            return 'all'
        clean = str(phone).replace(" ", "").replace("-", "").strip()
        if not clean.startswith("+"):
            clean = "+" + clean
        return clean

    @staticmethod
    def get_settings(user_id, raw_target='all'):
        target = AutoReplyManager.normalize_phone(raw_target)
        if not supabase:
            from local_data import get_local_auto_reply_settings
            return get_local_auto_reply_settings()

        res = supabase.table('auto_reply_settings').select("*")\
            .eq('user_id', user_id).eq('target_phone', target).execute()
        if res.data:
            return res.data[0]

        if target != 'all':
            res_glob = supabase.table('auto_reply_settings').select("*")\
                .eq('user_id', user_id).eq('target_phone', 'all').execute()
            if res_glob.data:
                return res_glob.data[0]

        return {
            'is_active': False,
            'cooldown_minutes': 60,
            'welcome_message': '',
            'target_phone': target
        }

    @staticmethod
    def update_settings(user_id, data):
        if not supabase:
            logger.warning("AutoReply: update_settings dipanggil tapi supabase tidak terhubung.")
            return
        try:
            data['target_phone'] = AutoReplyManager.normalize_phone(data.get('target_phone', 'all'))
            existing = supabase.table('auto_reply_settings').select("id")\
                .eq('user_id', user_id).eq('target_phone', data['target_phone']).execute()
            if existing.data:
                supabase.table('auto_reply_settings').update(data)\
                    .eq('id', existing.data[0]['id']).execute()
            else:
                data['user_id'] = user_id
                supabase.table('auto_reply_settings').insert(data).execute()
        except Exception as e:
            logger.error(f"AutoReply update_settings Error: {e}")

    @staticmethod
    def get_keywords(user_id):
        if not supabase:
            from local_data import get_local_keywords
            return get_local_keywords()
        try:
            res = supabase.table('keyword_rules').select("*")\
                .eq('user_id', user_id).order('created_at', desc=True).execute()
            return res.data if res.data else []
        except Exception as e:
            logger.error(f"AutoReply get_keywords Error: {e}")
            return []

    @staticmethod
    def add_keyword(user_id, keyword, response, raw_target='all'):
        if not supabase:
            logger.warning("AutoReply: add_keyword dipanggil tapi supabase tidak terhubung.")
            return
        try:
            target = AutoReplyManager.normalize_phone(raw_target)
            data = {
                'user_id': user_id,
                'keyword': keyword.lower(),
                'response': response,
                'target_phone': target
            }
            supabase.table('keyword_rules').insert(data).execute()
        except Exception as e:
            logger.error(f"AutoReply add_keyword Error: {e}")

    @staticmethod
    def delete_keyword(id, user_id=None):
        if not supabase:
            logger.warning("AutoReply: delete_keyword dipanggil tapi supabase tidak terhubung.")
            return
        try:
            query = supabase.table('keyword_rules').delete().eq('id', id)
            if user_id:
                query = query.eq('user_id', user_id)
            query.execute()
        except Exception as e:
            logger.error(f"AutoReply delete_keyword Error: {e}")

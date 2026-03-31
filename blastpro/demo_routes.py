from flask import Blueprint, render_template, redirect
from datetime import datetime, timedelta, timezone
import logging
import json

# Blueprint Setup
demo_bp = Blueprint('demo', __name__)
logger = logging.getLogger("BabaSaaSCore")

# --- DATA PALSU (DUMMY) ---
class DemoUserEntity:
    def __init__(self):
        self.id = 12345
        self.email = "demo.user@blastpro.id"
        self.is_admin = False
        self.is_banned = False
        self.created_at = datetime.utcnow()
        self.avatar_url = None
        self.plan_tier = 'UMKM Pro'
        self.wallet_balance = 750000
        self.phone_number = '+6281299998888'
        self.referral_code = 'DEMO123'
        self.username = 'demoblastpro'
        self.days_remaining = 28
        self.subscription_status = 'Active'
        self.sub_end_date = datetime.utcnow() + timedelta(days=28)
        self.notification_chat_id = None
        self.telegram_account = type('TeleInfo', (object,), {
            'phone_number': '+6281299998888',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'tele_users_count': 888
        })

def get_demo_data():
    now = datetime.now(timezone.utc) + timedelta(hours=7)  # WIB = UTC+7
    raw_targets = [
        {'id': 1, 'group_name': 'KASKUS KAMBOJA KPS', 'group_id': '100001', 'topic_ids': None, 'template_name': 'Promo Lebaran', 'source_phone': '+6281299998888', 'source_name': 'Demo Akun', 'created_at': now.isoformat()},
        {'id': 2, 'group_name': 'Fjb Kaskus Kps', 'group_id': '100002', 'topic_ids': '1,5', 'template_name': 'Promo Lebaran', 'source_phone': '+6281299998888', 'source_name': 'Demo Akun', 'created_at': now.isoformat()},
        {'id': 3, 'group_name': 'Info Loker Kamboja', 'group_id': '100003', 'topic_ids': '1,8', 'template_name': 'Promo Lebaran', 'source_phone': '+6281299998888', 'source_name': 'Demo Akun', 'created_at': now.isoformat()},
        {'id': 4, 'group_name': 'ALFAMART KPS POIPET', 'group_id': '100004', 'topic_ids': '1,3', 'template_name': 'Blast Harian', 'source_phone': '+6281299998888', 'source_name': 'Demo Akun', 'created_at': now.isoformat()},
        {'id': 5, 'group_name': 'KASKUS FJB POIPET', 'group_id': '100005', 'topic_ids': '1,7', 'template_name': 'Blast Harian', 'source_phone': '+6281299998888', 'source_name': 'Demo Akun', 'created_at': now.isoformat()},
    ]

    grouped_targets = {}
    for t in raw_targets:
        src = t.get('source_phone') or 'Unknown Account'
        tmpl = t.get('template_name') or 'Tanpa Nama'
        if src not in grouped_targets:
            grouped_targets[src] = {}
        if tmpl not in grouped_targets[src]:
            grouped_targets[src][tmpl] = []
        grouped_targets[src][tmpl].append(t)

    def make_log(id, group_name, status, delta_minutes=0, error=None):
        ts = now - timedelta(minutes=delta_minutes)
        return {
            'id': id,
            'group_name': group_name,
            'status': status,
            'created_at': ts.isoformat(),
            'wib_time': ts.strftime('%H:%M:%S'),
            'wib_date': ts.strftime('%Y-%m-%d'),
            'error_message': error
        }

    return {
        'logs': [
            make_log(1, 'KASKUS KAMBOJA KPS', 'success', 0),
            make_log(2, 'Fjb Kaskus Kps', 'success', 12),
            make_log(3, 'Info Loker Kamboja', 'success', 45),
            make_log(4, 'ALFAMART KPS POIPET', 'success', 62),
            make_log(5, 'Kaskus Cambodia', 'success', 95),
        ],
        'templates': [
            {'id': 1, 'name': 'Promo Diskon 50%', 'message_text': 'Halo kak, dapatkan diskon 50% khusus hari ini!'},
            {'id': 2, 'name': 'Restock Barang', 'message_text': 'Barang sudah ready stok lagi ya kak, silahkan order.'},
            {'id': 3, 'name': 'Ucapan Pagi', 'message_text': 'Selamat pagi kak, semangat beraktivitas!'}
        ],
        'schedules': [
            {'id': 1, 'run_hour': 8, 'run_minute': 0, 'is_active': True, 'template_id': 3, 'template_name': 'Ucapan Pagi', 'sender_phone': 'auto', 'target_template_name': 'Blast Harian'},
            {'id': 2, 'run_hour': 12, 'run_minute': 0, 'is_active': True, 'template_id': 1, 'template_name': 'Promo Diskon 50%', 'sender_phone': 'auto', 'target_template_name': 'Promo Lebaran'},
            {'id': 3, 'run_hour': 18, 'run_minute': 30, 'is_active': True, 'template_id': 2, 'template_name': 'Restock Barang', 'sender_phone': '+6281299998888', 'target_template_name': None},
        ],
        'targets': raw_targets,
        'grouped_targets': grouped_targets,
        'accounts': [{'id': 1, 'phone_number': '+6281299998888', 'first_name': 'Demo', 'last_name': 'Akun', 'username': 'demoblastpro', 'is_active': True}],
        'crm_count': 888,
        'crm_users': [
            {'user_id': 113211, 'first_name': 'Budi Santoso', 'username': 'bud1g4nt3n9', 'last_interaction': now.isoformat()},
            {'user_id': 221122, 'first_name': 'Siti Aminah', 'username': None, 'last_interaction': (now - timedelta(days=1)).isoformat()},
            {'user_id': 337783, 'first_name': 'Dracin Lovers', 'username': 'dr4mamu_b0t', 'last_interaction': (now - timedelta(days=2)).isoformat()},
        ],
        'keywords': [
            {'id': 1, 'keyword': 'harga', 'response': 'Harga mulai dari Rp 50.000, hubungi CS kami untuk info lebih lanjut.', 'target_phone': 'all'},
            {'id': 2, 'keyword': 'order', 'response': 'Untuk order silahkan klik link di bio ya kak!', 'target_phone': 'all'},
        ],
        'auto_reply_settings': {
            'is_active': True,
            'cooldown_minutes': 60,
            'welcome_message': 'Halo kak! Terima kasih sudah menghubungi kami. Ada yang bisa kami bantu? 😊',
            'target_phone': 'all'
        }
    }

# --- RUTE DEMO ---
@demo_bp.route('/live-demo/<path:page>')
def live_demo_view(page):
    try:
        data = get_demo_data()
        user = DemoUserEntity()
        
        # Inject variable wajib
        common = {
            'user': user, 
            'user_count': 888, 
            'is_demo_mode': True, 
            'selected_ids': None
        }

        if page == 'dashboard':
            return render_template('dashboard/index.html', **common,
                                   logs=data['logs'], schedules=data['schedules'], targets=data['targets'],
                                   accounts_list=data['accounts'],
                                   current_page=1, total_pages=1, per_page=5, total_logs=5,
                                   status_filter='all', date_filter='all',
                                   search_target='', sender_filter='',
                                   active_page='home')
            
        elif page == 'broadcast':
            return render_template('dashboard/broadcast.html', **common, 
                                   templates=data['templates'],
                                   accounts=data['accounts'],
                                   active_page='broadcast', count_selected=0)
            
        elif page == 'targets':
            return render_template('dashboard/targets.html', **common,
                                   grouped_targets=data['grouped_targets'],
                                   accounts=data['accounts'],
                                   active_page='targets')
            
        elif page == 'schedule':
            return render_template('dashboard/schedule.html', **common,
                                   schedules=data['schedules'],
                                   templates=data['templates'],
                                   targets=data['targets'],
                                   accounts=data['accounts'],
                                   active_page='schedule')
        
        elif page == 'crm':
             return render_template('dashboard/crm.html', **common, 
                                    crm_users=data['crm_users'], 
                                    active_page='crm',
                                    current_page=1, 
                                    total_pages=1, 
                                    per_page=10, 
                                    total_logs=len(data['crm_users']))

        elif page == 'connection':
             return render_template('dashboard/connection.html', **common,
                                    accounts=data['accounts'],
                                    active_page='connection')
             
        elif page == 'profile':
             return render_template('dashboard/profile.html', **common,
                                    active_page='profile',
                                    bot_link='#',
                                    is_notif_connected=False)
             
        elif page == 'templates':
             return render_template('dashboard/templates.html', **common,
                                    templates=data['templates'], active_page='templates')

        elif page in ('autoreply', 'auto-reply'):
            demo_phone = '+6281299998888'
            grouped_keywords = {
                'all': data['keywords'],
                demo_phone: []
            }
            settings_map = {
                demo_phone: data['auto_reply_settings']
            }
            return render_template('dashboard/auto_reply.html', **common,
                                   accounts=data['accounts'],
                                   grouped_keywords=grouped_keywords,
                                   settings_map=settings_map,
                                   active_phones_normalized=['all'],
                                   active_tab='all',
                                   settings=data['auto_reply_settings'],
                                   active_page='autoreply')

        elif page in ('payment', 'billing'):
            now_wib = datetime.now(timezone.utc) + timedelta(hours=7)
            starter_features = ['1 Akun Telegram', 'Broadcast Unlimited', 'CRM & Target Grup', 'Jadwal Otomatis', 'Template Pesan']
            pro_features = ['3 Akun Telegram', 'Semua Fitur Starter', 'Auto-Reply Keyword', 'Prioritas Support']
            agency_features = ['10 Akun Telegram', 'Semua Fitur Pro', 'Multi-Account Management', 'Dedicated Support']

            demo_plans = {
                'basic': [
                    {'id': 1, 'title': 'Bulanan', 'duration': '30 Hari', 'price': 'Rp 150.000', 'rawPrice': 150000,
                     'coret': 'Rp 250.000', 'hemat': 'Hemat 40%', 'features': starter_features, 'btnText': 'Pilih Paket', 'bestValue': False},
                    {'id': 2, 'title': 'Quarterly', 'duration': '90 Hari', 'price': 'Rp 350.000', 'rawPrice': 350000,
                     'coret': 'Rp 750.000', 'hemat': 'Hemat 53%', 'features': starter_features, 'btnText': 'Pilih Paket', 'bestValue': True},
                    {'id': 3, 'title': 'Semester', 'duration': '180 Hari', 'price': 'Rp 600.000', 'rawPrice': 600000,
                     'coret': 'Rp 1.500.000', 'hemat': 'Hemat 60%', 'features': starter_features, 'btnText': 'Pilih Paket', 'bestValue': False},
                ],
                'optimal': [
                    {'id': 4, 'title': 'Bulanan', 'duration': '30 Hari', 'price': 'Rp 350.000', 'rawPrice': 350000,
                     'coret': 'Rp 500.000', 'hemat': 'Hemat 30%', 'features': pro_features, 'btnText': 'Pilih Paket', 'bestValue': False},
                    {'id': 5, 'title': 'Quarterly', 'duration': '90 Hari', 'price': 'Rp 800.000', 'rawPrice': 800000,
                     'coret': 'Rp 1.500.000', 'hemat': 'Hemat 47%', 'features': pro_features, 'btnText': 'Pilih Paket', 'bestValue': True},
                    {'id': 6, 'title': 'Semester', 'duration': '180 Hari', 'price': 'Rp 1.400.000', 'rawPrice': 1400000,
                     'coret': 'Rp 3.000.000', 'hemat': 'Hemat 53%', 'features': pro_features, 'btnText': 'Pilih Paket', 'bestValue': False},
                ],
                'agency': [
                    {'id': 7, 'title': 'Bulanan', 'duration': '30 Hari', 'price': 'Rp 750.000', 'rawPrice': 750000,
                     'coret': 'Rp 1.200.000', 'hemat': 'Hemat 37%', 'features': agency_features, 'btnText': 'Pilih Paket', 'bestValue': False},
                    {'id': 8, 'title': 'Quarterly', 'duration': '90 Hari', 'price': 'Rp 1.800.000', 'rawPrice': 1800000,
                     'coret': 'Rp 3.600.000', 'hemat': 'Hemat 50%', 'features': agency_features, 'btnText': 'Pilih Paket', 'bestValue': True},
                    {'id': 9, 'title': 'Semester', 'duration': '180 Hari', 'price': 'Rp 3.000.000', 'rawPrice': 3000000,
                     'coret': 'Rp 7.200.000', 'hemat': 'Hemat 1.2 Juta', 'features': agency_features, 'btnText': 'Pilih Paket', 'bestValue': False},
                ],
            }

            demo_banks = [
                {'id': 1, 'bank_name': 'BCA', 'account_number': '1234567890', 'account_holder': 'PT BLASTPRO INDONESIA', 'is_active': True},
                {'id': 2, 'bank_name': 'Mandiri', 'account_number': '9876543210', 'account_holder': 'PT BLASTPRO INDONESIA', 'is_active': True},
                {'id': 3, 'bank_name': 'GoPay / OVO / DANA', 'account_number': '+6281234567890', 'account_holder': 'BLASTPRO OFFICIAL', 'is_active': True},
            ]

            demo_transactions = [
                {
                    'id': 'a1b2c3d4-demo-0001',
                    'amount': 800000,
                    'status': 'approved',
                    'payment_method': 'BCA',
                    'proof_url': None,
                    'admin_note': 'Pembayaran diterima. Terima kasih!',
                    'created_at': (now_wib - timedelta(days=62)).isoformat(),
                    'pricing_variants': {'duration_days': 90, 'pricing_plans': {'display_name': 'UMKM Pro'}}
                },
                {
                    'id': 'e5f6a7b8-demo-0002',
                    'amount': 350000,
                    'status': 'approved',
                    'payment_method': 'Mandiri',
                    'proof_url': None,
                    'admin_note': 'Sudah diverifikasi.',
                    'created_at': (now_wib - timedelta(days=155)).isoformat(),
                    'pricing_variants': {'duration_days': 30, 'pricing_plans': {'display_name': 'Starter'}}
                },
                {
                    'id': 'c9d0e1f2-demo-0003',
                    'amount': 150000,
                    'status': 'rejected',
                    'payment_method': 'BCA',
                    'proof_url': None,
                    'admin_note': 'Bukti transfer tidak jelas. Silakan kirim ulang.',
                    'created_at': (now_wib - timedelta(days=200)).isoformat(),
                    'pricing_variants': {'duration_days': 30, 'pricing_plans': {'display_name': 'Starter'}}
                },
            ]

            return render_template('dashboard/payment.html', **common,
                                   active_page='payment',
                                   plans_json=json.dumps(demo_plans),
                                   banks=demo_banks,
                                   transactions=demo_transactions,
                                   has_pending=False)

        else:
            return redirect('/live-demo/dashboard')
            
    except Exception as e:
        logger.error(f"Demo View Error: {e}")
        return f"<h2 style='color:red; text-align:center; margin-top:50px;'>Demo Error: {str(e)}</h2>"

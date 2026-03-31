"""
Data contoh lokal lengkap untuk user@blastpro.id saat Supabase tidak terhubung.
"""
from datetime import datetime, timedelta, timezone

def _now():
    return datetime.now(timezone.utc) + timedelta(hours=7)


def get_local_accounts():
    now = _now()
    return [
        {
            'id': 1,
            'phone_number': '+6281234567890',
            'first_name': 'Budi',
            'last_name': 'Santoso',
            'username': 'budi_blastpro',
            'is_active': True,
            'created_at': (now - timedelta(days=30)).isoformat()
        },
        {
            'id': 2,
            'phone_number': '+6281298765432',
            'first_name': 'Toko',
            'last_name': 'Online',
            'username': 'tokoonline_id',
            'is_active': True,
            'created_at': (now - timedelta(days=20)).isoformat()
        },
        {
            'id': 3,
            'phone_number': '+6285612349876',
            'first_name': 'Rina',
            'last_name': 'Widyaningsih',
            'username': 'rinawd_shop',
            'is_active': True,
            'created_at': (now - timedelta(days=12)).isoformat()
        },
        {
            'id': 4,
            'phone_number': '+6287765432100',
            'first_name': 'Promo',
            'last_name': 'Akun',
            'username': 'promo_akun_id',
            'is_active': False,
            'created_at': (now - timedelta(days=5)).isoformat()
        },
    ]


def get_local_templates():
    now = _now()
    return [
        {
            'id': 1,
            'name': 'Promo Diskon 50%',
            'message_text': 'Halo {name}! 🎉\n\nKabar gembira! Kami sedang mengadakan PROMO BESAR-BESARAN diskon hingga 50% untuk semua produk pilihan.\n\n✅ Promo berlaku hari ini saja!\n✅ Stok terbatas\n✅ Gratis ongkir min. order 100rb\n\nSegera order sekarang sebelum kehabisan! 🛒',
            'source_chat_id': None, 'source_message_id': None,
            'created_at': (now - timedelta(days=30)).isoformat(), 'user_id': 'local-user'
        },
        {
            'id': 2,
            'name': 'Restock Barang Baru',
            'message_text': 'Halo {name}! 📦\n\nKabar gembira! Stok barang favorit kamu sudah READY lagi nih!\n\n🆕 Produk baru sudah tersedia\n📲 Order via DM atau klik link di bio\n🚀 Pengiriman same day untuk order sebelum jam 12 siang\n\nJangan sampai kehabisan lagi ya! 😊',
            'source_chat_id': None, 'source_message_id': None,
            'created_at': (now - timedelta(days=25)).isoformat(), 'user_id': 'local-user'
        },
        {
            'id': 3,
            'name': 'Ucapan Selamat Pagi',
            'message_text': 'Selamat pagi {name}! ☀️\n\nSemangat menjalani hari ini ya! Jangan lupa cek produk terbaru kami yang pastinya bermanfaat untuk kamu.\n\n💫 Tetap produktif & sehat!\n\n#SemangatPagi #BlastPro',
            'source_chat_id': None, 'source_message_id': None,
            'created_at': (now - timedelta(days=20)).isoformat(), 'user_id': 'local-user'
        },
        {
            'id': 4,
            'name': 'Follow Up Order',
            'message_text': 'Halo {name}! 👋\n\nKami ingin memastikan pesanan Anda sudah diterima dengan baik.\n\n📦 Status: Terkirim\n⭐ Jika puas, mohon berikan ulasan ya!\n\nAda yang bisa kami bantu? Hubungi CS kami 24/7. 😊',
            'source_chat_id': None, 'source_message_id': None,
            'created_at': (now - timedelta(days=18)).isoformat(), 'user_id': 'local-user'
        },
        {
            'id': 5,
            'name': 'Flash Sale Weekend',
            'message_text': 'Halo {name}! ⚡\n\nFLASH SALE WEEKEND sudah dimulai!\n\n🔥 Diskon 70% produk tertentu\n🕐 Hanya 24 jam mulai hari ini!\n🎁 Bonus hadiah untuk pembelian pertama\n\nBuruan sebelum HABIS! 😱\n\n👉 Chat kami sekarang!',
            'source_chat_id': None, 'source_message_id': None,
            'created_at': (now - timedelta(days=15)).isoformat(), 'user_id': 'local-user'
        },
        {
            'id': 6,
            'name': 'Promo Ramadhan',
            'message_text': 'Assalamualaikum {name}! 🌙\n\nSambut Ramadhan dengan penawaran spesial dari kami!\n\n🎊 Diskon 40% semua produk\n🎁 Hadiah gratis untuk pembelian di atas 500rb\n🚚 Gratis ongkir ke seluruh Indonesia\n\nRaih keberkahan Ramadhan bersama kami! ✨',
            'source_chat_id': None, 'source_message_id': None,
            'created_at': (now - timedelta(days=12)).isoformat(), 'user_id': 'local-user'
        },
        {
            'id': 7,
            'name': 'Blast Mingguan',
            'message_text': 'Halo {name}! 📢\n\nUpdate mingguan produk terbaik kami sudah tiba!\n\n📌 Produk terlaris minggu ini:\n1. Item A - Rp 75.000\n2. Item B - Rp 120.000\n3. Item C - Rp 55.000\n\n💬 Chat kami untuk pemesanan. Terima kasih! 🙏',
            'source_chat_id': None, 'source_message_id': None,
            'created_at': (now - timedelta(days=10)).isoformat(), 'user_id': 'local-user'
        },
        {
            'id': 8,
            'name': 'Update Stok Produk',
            'message_text': 'Halo {name}! 🛍️\n\nStok produk terbaru kami telah di-update!\n\n✅ Tersedia dalam berbagai pilihan warna\n✅ Ukuran S hingga XL tersedia\n✅ Bahan premium berkualitas tinggi\n\n📲 Segera pesan sebelum kehabisan!\nHubungi kami via chat ya! 😊',
            'source_chat_id': None, 'source_message_id': None,
            'created_at': (now - timedelta(days=8)).isoformat(), 'user_id': 'local-user'
        },
        {
            'id': 9,
            'name': 'Iklan Produk Baru',
            'message_text': 'Halo {name}! 🆕\n\nProduk BARU kami resmi diluncurkan hari ini!\n\n🌟 Fitur unggulan:\n- Kualitas premium terjangkau\n- Garansi 1 tahun\n- Support purna jual 24/7\n\nJadi yang PERTAMA memilikinya!\n👉 DM kami sekarang untuk pre-order!',
            'source_chat_id': None, 'source_message_id': None,
            'created_at': (now - timedelta(days=5)).isoformat(), 'user_id': 'local-user'
        },
        {
            'id': 10,
            'name': 'Selamat Malam Closing',
            'message_text': 'Selamat malam {name}! 🌙\n\nSebelum tidur, jangan lupa checkout produk yang sudah kamu simpan di keranjang ya!\n\n🛒 Stok bisa habis kapan saja\n⏰ Promo berakhir tengah malam\n\nSalam sukses & istirahat yang nyaman! 😴',
            'source_chat_id': None, 'source_message_id': None,
            'created_at': (now - timedelta(days=3)).isoformat(), 'user_id': 'local-user'
        },
        {
            'id': 11,
            'name': 'Testimoni & Review',
            'message_text': 'Halo {name}! ⭐⭐⭐⭐⭐\n\n"Produknya luar biasa! Kualitas premium, pengiriman cepat, dan CS sangat responsif. Pasti repeat order!" - Pelanggan setia kami\n\n📸 Lihat lebih banyak testimoni di highlight Instagram kami\n\n🛒 Dapatkan produk terbaik kami sekarang!',
            'source_chat_id': None, 'source_message_id': None,
            'created_at': (now - timedelta(days=1)).isoformat(), 'user_id': 'local-user'
        },
        {
            'id': 12,
            'name': 'Akhir Bulan Promo',
            'message_text': 'Halo {name}! 🎯\n\nPROGRAM AKHIR BULAN spesial untuk kamu!\n\n💰 Belanja min 200rb → Cashback 20rb\n💰 Belanja min 500rb → Cashback 75rb\n💰 Belanja min 1jt → Cashback 200rb\n\nPromo hanya berlaku s.d. akhir bulan ini!\nJangan lewatkan ya kak! 🔔',
            'source_chat_id': None, 'source_message_id': None,
            'created_at': (now - timedelta(hours=12)).isoformat(), 'user_id': 'local-user'
        },
    ]


def get_local_targets():
    now = _now()
    return [
        # ── Promo Harian (Budi)
        {'id': 1,  'group_name': 'Grup Jual Beli Jakarta',           'group_id': '-1001234567001', 'topic_ids': None,   'template_name': 'Promo Harian',       'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=30)).isoformat(), 'user_id': 'local-user'},
        {'id': 2,  'group_name': 'FJB Bandung Official',             'group_id': '-1001234567002', 'topic_ids': '1,5',  'template_name': 'Promo Harian',       'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=30)).isoformat(), 'user_id': 'local-user'},
        {'id': 3,  'group_name': 'Info Loker Surabaya',              'group_id': '-1001234567003', 'topic_ids': '1,8',  'template_name': 'Promo Harian',       'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=28)).isoformat(), 'user_id': 'local-user'},
        {'id': 4,  'group_name': 'Komunitas UMKM Yogyakarta',        'group_id': '-1001234567004', 'topic_ids': None,   'template_name': 'Promo Harian',       'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=27)).isoformat(), 'user_id': 'local-user'},
        {'id': 5,  'group_name': 'Toko Online Semarang',             'group_id': '-1001234567005', 'topic_ids': '1,3',  'template_name': 'Promo Harian',       'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=25)).isoformat(), 'user_id': 'local-user'},
        {'id': 6,  'group_name': 'FJB Depok & Bekasi',               'group_id': '-1001234567050', 'topic_ids': '2,4',  'template_name': 'Promo Harian',       'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=24)).isoformat(), 'user_id': 'local-user'},
        {'id': 7,  'group_name': 'Jual Beli Bogor Raya',             'group_id': '-1001234567051', 'topic_ids': None,   'template_name': 'Promo Harian',       'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=23)).isoformat(), 'user_id': 'local-user'},
        {'id': 8,  'group_name': 'Olshop Tangerang Selatan',         'group_id': '-1001234567052', 'topic_ids': None,   'template_name': 'Promo Harian',       'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=22)).isoformat(), 'user_id': 'local-user'},
        {'id': 9,  'group_name': 'Pedagang Pasar Baru Jakarta',      'group_id': '-1001234567053', 'topic_ids': '2,3',  'template_name': 'Promo Harian',       'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=21)).isoformat(), 'user_id': 'local-user'},
        {'id': 10, 'group_name': 'Komunitas Dropshipper Jakarta',    'group_id': '-1001234567054', 'topic_ids': None,   'template_name': 'Promo Harian',       'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=20)).isoformat(), 'user_id': 'local-user'},
        # ── Blast Mingguan (Toko Online)
        {'id': 11, 'group_name': 'Marketplace Medan Group',          'group_id': '-1001234567006', 'topic_ids': None,   'template_name': 'Blast Mingguan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(days=20)).isoformat(), 'user_id': 'local-user'},
        {'id': 12, 'group_name': 'Pedagang Online Makassar',         'group_id': '-1001234567007', 'topic_ids': '1,2',  'template_name': 'Blast Mingguan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(days=19)).isoformat(), 'user_id': 'local-user'},
        {'id': 13, 'group_name': 'FJB Palembang Resmi',              'group_id': '-1001234567008', 'topic_ids': None,   'template_name': 'Blast Mingguan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(days=18)).isoformat(), 'user_id': 'local-user'},
        {'id': 14, 'group_name': 'Komunitas Bisnis Balikpapan',      'group_id': '-1001234567060', 'topic_ids': '1,3',  'template_name': 'Blast Mingguan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(days=17)).isoformat(), 'user_id': 'local-user'},
        {'id': 15, 'group_name': 'Jualan Online Pontianak',          'group_id': '-1001234567061', 'topic_ids': None,   'template_name': 'Blast Mingguan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(days=16)).isoformat(), 'user_id': 'local-user'},
        {'id': 16, 'group_name': 'FJB Samarinda & Kukar',            'group_id': '-1001234567062', 'topic_ids': '2,5',  'template_name': 'Blast Mingguan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(days=15)).isoformat(), 'user_id': 'local-user'},
        {'id': 17, 'group_name': 'Reseller Nasional Aktif',          'group_id': '-1001234567063', 'topic_ids': None,   'template_name': 'Blast Mingguan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(days=14)).isoformat(), 'user_id': 'local-user'},
        {'id': 18, 'group_name': 'Dropshipper Sulawesi Selatan',     'group_id': '-1001234567064', 'topic_ids': '1,4',  'template_name': 'Blast Mingguan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(days=13)).isoformat(), 'user_id': 'local-user'},
        # ── Flash Sale Weekend (Budi)
        {'id': 19, 'group_name': 'Grup Flash Sale Indonesia',        'group_id': '-1001234567070', 'topic_ids': None,   'template_name': 'Flash Sale Weekend', 'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=13)).isoformat(), 'user_id': 'local-user'},
        {'id': 20, 'group_name': 'Promo Murah Jakarta Selatan',      'group_id': '-1001234567071', 'topic_ids': '1,6',  'template_name': 'Flash Sale Weekend', 'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=12)).isoformat(), 'user_id': 'local-user'},
        {'id': 21, 'group_name': 'Diskon Hari Ini Surabaya',         'group_id': '-1001234567072', 'topic_ids': '1,4',  'template_name': 'Flash Sale Weekend', 'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=11)).isoformat(), 'user_id': 'local-user'},
        {'id': 22, 'group_name': 'Jual Murah Bandung Raya',          'group_id': '-1001234567073', 'topic_ids': None,   'template_name': 'Flash Sale Weekend', 'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=10)).isoformat(), 'user_id': 'local-user'},
        {'id': 23, 'group_name': 'Weekend Deal Yogyakarta',          'group_id': '-1001234567074', 'topic_ids': None,   'template_name': 'Flash Sale Weekend', 'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=9)).isoformat(),  'user_id': 'local-user'},
        {'id': 24, 'group_name': 'Sale Elektronik Semarang',         'group_id': '-1001234567075', 'topic_ids': '3,7',  'template_name': 'Flash Sale Weekend', 'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=8)).isoformat(),  'user_id': 'local-user'},
        # ── Update Stok Produk (Rina)
        {'id': 25, 'group_name': 'Reseller Baju Grosir Tanah Abang', 'group_id': '-1001234567080', 'topic_ids': None,   'template_name': 'Update Stok Produk', 'source_phone': '+6285612349876', 'source_name': 'Rina Widyaningsih','created_at': (now - timedelta(days=8)).isoformat(),  'user_id': 'local-user'},
        {'id': 26, 'group_name': 'Dropship Tas & Sepatu',            'group_id': '-1001234567081', 'topic_ids': '1,2',  'template_name': 'Update Stok Produk', 'source_phone': '+6285612349876', 'source_name': 'Rina Widyaningsih','created_at': (now - timedelta(days=7)).isoformat(),  'user_id': 'local-user'},
        {'id': 27, 'group_name': 'Agen Kosmetik Murah Bandung',      'group_id': '-1001234567082', 'topic_ids': None,   'template_name': 'Update Stok Produk', 'source_phone': '+6285612349876', 'source_name': 'Rina Widyaningsih','created_at': (now - timedelta(days=6)).isoformat(),  'user_id': 'local-user'},
        {'id': 28, 'group_name': 'Distributor Sembako Nasional',     'group_id': '-1001234567083', 'topic_ids': '2,3',  'template_name': 'Update Stok Produk', 'source_phone': '+6285612349876', 'source_name': 'Rina Widyaningsih','created_at': (now - timedelta(days=5)).isoformat(),  'user_id': 'local-user'},
        {'id': 29, 'group_name': 'Supplier Elektronik Surabaya',     'group_id': '-1001234567084', 'topic_ids': None,   'template_name': 'Update Stok Produk', 'source_phone': '+6285612349876', 'source_name': 'Rina Widyaningsih','created_at': (now - timedelta(days=5)).isoformat(),  'user_id': 'local-user'},
        {'id': 30, 'group_name': 'Grosir Fashion Muslim Jakarta',    'group_id': '-1001234567085', 'topic_ids': '1,5',  'template_name': 'Update Stok Produk', 'source_phone': '+6285612349876', 'source_name': 'Rina Widyaningsih','created_at': (now - timedelta(days=4)).isoformat(),  'user_id': 'local-user'},
        # ── Iklan Produk Baru (Budi)
        {'id': 31, 'group_name': 'Komunitas Startup Jaksel',         'group_id': '-1001234567090', 'topic_ids': None,   'template_name': 'Iklan Produk Baru',  'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=4)).isoformat(),  'user_id': 'local-user'},
        {'id': 32, 'group_name': 'Tech & Gadget Indonesia',          'group_id': '-1001234567091', 'topic_ids': '1,5',  'template_name': 'Iklan Produk Baru',  'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=3)).isoformat(),  'user_id': 'local-user'},
        {'id': 33, 'group_name': 'Penggemar Produk Lokal',           'group_id': '-1001234567092', 'topic_ids': None,   'template_name': 'Iklan Produk Baru',  'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=3)).isoformat(),  'user_id': 'local-user'},
        {'id': 34, 'group_name': 'UMKM Digital Nusantara',           'group_id': '-1001234567093', 'topic_ids': '2,6',  'template_name': 'Iklan Produk Baru',  'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=2)).isoformat(),  'user_id': 'local-user'},
        {'id': 35, 'group_name': 'Wirausaha Muda Indonesia',         'group_id': '-1001234567094', 'topic_ids': None,   'template_name': 'Iklan Produk Baru',  'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(days=2)).isoformat(),  'user_id': 'local-user'},
        # ── Promo Ramadhan (Toko Online)
        {'id': 36, 'group_name': 'Bazaar Ramadhan Jakarta',          'group_id': '-1001234567100', 'topic_ids': None,   'template_name': 'Promo Ramadhan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(days=2)).isoformat(),  'user_id': 'local-user'},
        {'id': 37, 'group_name': 'Baju Muslim Grosir Surabaya',      'group_id': '-1001234567101', 'topic_ids': '1,3',  'template_name': 'Promo Ramadhan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(days=2)).isoformat(),  'user_id': 'local-user'},
        {'id': 38, 'group_name': 'Hampers Lebaran Murah',            'group_id': '-1001234567102', 'topic_ids': None,   'template_name': 'Promo Ramadhan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(days=1)).isoformat(),  'user_id': 'local-user'},
        {'id': 39, 'group_name': 'Jualan Online Ramadhan Sale',      'group_id': '-1001234567103', 'topic_ids': '2,4',  'template_name': 'Promo Ramadhan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(days=1)).isoformat(),  'user_id': 'local-user'},
        {'id': 40, 'group_name': 'Promo Sahur & Buka Puasa',         'group_id': '-1001234567104', 'topic_ids': None,   'template_name': 'Promo Ramadhan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(hours=20)).isoformat(), 'user_id': 'local-user'},
        {'id': 41, 'group_name': 'Takjil & Kue Lebaran Murah',       'group_id': '-1001234567105', 'topic_ids': '1,2',  'template_name': 'Promo Ramadhan',     'source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(hours=18)).isoformat(), 'user_id': 'local-user'},
        # ── Akhir Bulan Promo (Rina)
        {'id': 42, 'group_name': 'Belanja Hemat Malang',             'group_id': '-1001234567110', 'topic_ids': None,   'template_name': 'Akhir Bulan Promo',  'source_phone': '+6285612349876', 'source_name': 'Rina Widyaningsih','created_at': (now - timedelta(hours=15)).isoformat(), 'user_id': 'local-user'},
        {'id': 43, 'group_name': 'Promo Akhir Bulan Surabaya',       'group_id': '-1001234567111', 'topic_ids': '3,5',  'template_name': 'Akhir Bulan Promo',  'source_phone': '+6285612349876', 'source_name': 'Rina Widyaningsih','created_at': (now - timedelta(hours=14)).isoformat(), 'user_id': 'local-user'},
        {'id': 44, 'group_name': 'Sale Besar Tangerang',             'group_id': '-1001234567112', 'topic_ids': None,   'template_name': 'Akhir Bulan Promo',  'source_phone': '+6285612349876', 'source_name': 'Rina Widyaningsih','created_at': (now - timedelta(hours=12)).isoformat(), 'user_id': 'local-user'},
        {'id': 45, 'group_name': 'Cashback Gede Bekasi',             'group_id': '-1001234567113', 'topic_ids': '1,4',  'template_name': 'Akhir Bulan Promo',  'source_phone': '+6285612349876', 'source_name': 'Rina Widyaningsih','created_at': (now - timedelta(hours=10)).isoformat(), 'user_id': 'local-user'},
        # ── Testimoni (Budi)
        {'id': 46, 'group_name': 'Komunitas Pembeli Cerdas',         'group_id': '-1001234567120', 'topic_ids': None,   'template_name': 'Testimoni & Review', 'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(hours=8)).isoformat(),  'user_id': 'local-user'},
        {'id': 47, 'group_name': 'Review Produk Indonesia',          'group_id': '-1001234567121', 'topic_ids': '2,3',  'template_name': 'Testimoni & Review', 'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(hours=6)).isoformat(),  'user_id': 'local-user'},
        {'id': 48, 'group_name': 'Testimoni Pelanggan Setia',        'group_id': '-1001234567122', 'topic_ids': None,   'template_name': 'Testimoni & Review', 'source_phone': '+6281234567890', 'source_name': 'Budi Santoso',   'created_at': (now - timedelta(hours=4)).isoformat(),  'user_id': 'local-user'},
        # ── Selamat Pagi (Toko Online)
        {'id': 49, 'group_name': 'Member VIP Toko Kami',             'group_id': '-1001234567130', 'topic_ids': None,   'template_name': 'Ucapan Selamat Pagi','source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(hours=2)).isoformat(),  'user_id': 'local-user'},
        {'id': 50, 'group_name': 'Pelanggan Loyal Batch 1',          'group_id': '-1001234567131', 'topic_ids': '1,2',  'template_name': 'Ucapan Selamat Pagi','source_phone': '+6281298765432', 'source_name': 'Toko Online',    'created_at': (now - timedelta(hours=1)).isoformat(),  'user_id': 'local-user'},
    ]


def get_local_grouped_targets():
    all_targets = get_local_targets()
    grouped = {}
    for t in all_targets:
        src = t.get('source_phone') or 'Unknown Account'
        tmpl = t.get('template_name') or 'Tanpa Nama'
        if src not in grouped:
            grouped[src] = {}
        if tmpl not in grouped[src]:
            grouped[src][tmpl] = []
        grouped[src][tmpl].append(t)
    return grouped


def get_local_schedules():
    return [
        {
            'id': 1, 'run_hour': 7, 'run_minute': 0, 'is_active': True,
            'template_id': 3, 'template_name': 'Ucapan Selamat Pagi',
            'sender_phone': 'auto', 'target_template_name': 'Promo Harian', 'user_id': 'local-user'
        },
        {
            'id': 2, 'run_hour': 9, 'run_minute': 30, 'is_active': True,
            'template_id': 1, 'template_name': 'Promo Diskon 50%',
            'sender_phone': '+6281234567890', 'target_template_name': 'Promo Harian', 'user_id': 'local-user'
        },
        {
            'id': 3, 'run_hour': 12, 'run_minute': 0, 'is_active': True,
            'template_id': 7, 'template_name': 'Blast Mingguan',
            'sender_phone': '+6281298765432', 'target_template_name': 'Blast Mingguan', 'user_id': 'local-user'
        },
        {
            'id': 4, 'run_hour': 14, 'run_minute': 0, 'is_active': True,
            'template_id': 5, 'template_name': 'Flash Sale Weekend',
            'sender_phone': 'auto', 'target_template_name': 'Flash Sale Weekend', 'user_id': 'local-user'
        },
        {
            'id': 5, 'run_hour': 16, 'run_minute': 30, 'is_active': True,
            'template_id': 2, 'template_name': 'Restock Barang Baru',
            'sender_phone': '+6285612349876', 'target_template_name': 'Update Stok Produk', 'user_id': 'local-user'
        },
        {
            'id': 6, 'run_hour': 19, 'run_minute': 0, 'is_active': True,
            'template_id': 10, 'template_name': 'Selamat Malam Closing',
            'sender_phone': '+6281234567890', 'target_template_name': 'Iklan Produk Baru', 'user_id': 'local-user'
        },
        {
            'id': 7, 'run_hour': 20, 'run_minute': 0, 'is_active': False,
            'template_id': 4, 'template_name': 'Follow Up Order',
            'sender_phone': '+6281298765432', 'target_template_name': None, 'user_id': 'local-user'
        },
        {
            'id': 8, 'run_hour': 21, 'run_minute': 30, 'is_active': False,
            'template_id': 12, 'template_name': 'Akhir Bulan Promo',
            'sender_phone': 'auto', 'target_template_name': 'Akhir Bulan Promo', 'user_id': 'local-user'
        },
    ]


def get_local_crm_users():
    now = _now()
    return [
        {'id': 1,  'user_id': 101234001, 'first_name': 'Budi',       'last_name': 'Santoso',      'username': 'budi_s99',        'phone': None, 'source_phone': '+6281234567890', 'last_interaction': now.isoformat()},
        {'id': 2,  'user_id': 101234002, 'first_name': 'Siti',       'last_name': 'Aminah Rahayu','username': None,              'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(hours=1)).isoformat()},
        {'id': 3,  'user_id': 101234003, 'first_name': 'Doni',       'last_name': 'Prasetyo',     'username': 'donipras',        'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(hours=2)).isoformat()},
        {'id': 4,  'user_id': 101234004, 'first_name': 'Rina',       'last_name': 'Widyaningsih', 'username': 'rinawd_shop',     'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(hours=3)).isoformat()},
        {'id': 5,  'user_id': 101234005, 'first_name': 'Ahmad',      'last_name': 'Fauzi',        'username': None,              'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(hours=4)).isoformat()},
        {'id': 6,  'user_id': 101234006, 'first_name': 'Dewi',       'last_name': 'Lestari Kusuma','username': 'dewilestari_id',  'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(hours=5)).isoformat()},
        {'id': 7,  'user_id': 101234007, 'first_name': 'Rizky',      'last_name': 'Ramadan',      'username': 'rizky_rd',        'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(hours=6)).isoformat()},
        {'id': 8,  'user_id': 101234008, 'first_name': 'Nurul',      'last_name': 'Hidayah',      'username': None,              'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(hours=8)).isoformat()},
        {'id': 9,  'user_id': 101234009, 'first_name': 'Eko',        'last_name': 'Wahyudi Santosa','username': 'eko_ws',         'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(hours=10)).isoformat()},
        {'id': 10, 'user_id': 101234010, 'first_name': 'Fitri',      'last_name': 'Handayani',    'username': 'fitrihandayani',  'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(hours=12)).isoformat()},
        {'id': 11, 'user_id': 101234011, 'first_name': 'Hendra',     'last_name': 'Gunawan',      'username': 'hendra_gw',       'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(hours=14)).isoformat()},
        {'id': 12, 'user_id': 101234012, 'first_name': 'Yuliana',    'last_name': 'Permata',      'username': None,              'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(hours=16)).isoformat()},
        {'id': 13, 'user_id': 101234013, 'first_name': 'Rudi',       'last_name': 'Kurniawan',    'username': 'rudi_kurn',       'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(hours=18)).isoformat()},
        {'id': 14, 'user_id': 101234014, 'first_name': 'Maya',       'last_name': 'Anggraeni',    'username': 'maya_angg',       'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(hours=20)).isoformat()},
        {'id': 15, 'user_id': 101234015, 'first_name': 'Fajar',      'last_name': 'Nugroho',      'username': None,              'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(hours=22)).isoformat()},
        {'id': 16, 'user_id': 101234016, 'first_name': 'Indah',      'last_name': 'Sari',         'username': 'indahsari_shop',  'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(days=1)).isoformat()},
        {'id': 17, 'user_id': 101234017, 'first_name': 'Bagas',      'last_name': 'Pramudita',    'username': 'bagas_pram',      'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(days=1, hours=2)).isoformat()},
        {'id': 18, 'user_id': 101234018, 'first_name': 'Ayu',        'last_name': 'Wulandari',    'username': None,              'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(days=1, hours=4)).isoformat()},
        {'id': 19, 'user_id': 101234019, 'first_name': 'Galih',      'last_name': 'Setiawan',     'username': 'galih_set',       'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(days=1, hours=6)).isoformat()},
        {'id': 20, 'user_id': 101234020, 'first_name': 'Putri',      'last_name': 'Maharani',     'username': 'putri_mhr',       'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(days=1, hours=8)).isoformat()},
        {'id': 21, 'user_id': 101234021, 'first_name': 'Wahyu',      'last_name': 'Pratama',      'username': None,              'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(days=2)).isoformat()},
        {'id': 22, 'user_id': 101234022, 'first_name': 'Laras',      'last_name': 'Kusumawati',   'username': 'laras_kw',        'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(days=2, hours=3)).isoformat()},
        {'id': 23, 'user_id': 101234023, 'first_name': 'Dimas',      'last_name': 'Aditya',       'username': 'dimas_adt',       'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(days=2, hours=6)).isoformat()},
        {'id': 24, 'user_id': 101234024, 'first_name': 'Novita',     'last_name': 'Rahmawati',    'username': None,              'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(days=3)).isoformat()},
        {'id': 25, 'user_id': 101234025, 'first_name': 'Agus',       'last_name': 'Hermawan',     'username': 'agus_hrm',        'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(days=3, hours=5)).isoformat()},
        {'id': 26, 'user_id': 101234026, 'first_name': 'Trisna',     'last_name': 'Dewi',         'username': 'trisna_d',        'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(days=4)).isoformat()},
        {'id': 27, 'user_id': 101234027, 'first_name': 'Yudi',       'last_name': 'Laksono',      'username': None,              'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(days=4, hours=3)).isoformat()},
        {'id': 28, 'user_id': 101234028, 'first_name': 'Nia',        'last_name': 'Kusuma',       'username': 'nia_kus',         'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(days=4, hours=8)).isoformat()},
        {'id': 29, 'user_id': 101234029, 'first_name': 'Hendro',     'last_name': 'Wijayanto',    'username': 'hendro_wj',       'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(days=5)).isoformat()},
        {'id': 30, 'user_id': 101234030, 'first_name': 'Sari',       'last_name': 'Puspitasari',  'username': None,              'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(days=5, hours=6)).isoformat()},
        {'id': 31, 'user_id': 101234031, 'first_name': 'Bambang',    'last_name': 'Suryanto',     'username': 'bambang_sry',     'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(days=6)).isoformat()},
        {'id': 32, 'user_id': 101234032, 'first_name': 'Lina',       'last_name': 'Marlina',      'username': 'lina_mrl',        'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(days=6, hours=4)).isoformat()},
        {'id': 33, 'user_id': 101234033, 'first_name': 'Kevin',      'last_name': 'Wijaya',       'username': None,              'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(days=7)).isoformat()},
        {'id': 34, 'user_id': 101234034, 'first_name': 'Suci',       'last_name': 'Rahayu',       'username': 'suci_rhy',        'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(days=7, hours=2)).isoformat()},
        {'id': 35, 'user_id': 101234035, 'first_name': 'Ferry',      'last_name': 'Adriansyah',   'username': 'ferry_adn',       'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(days=8)).isoformat()},
        {'id': 36, 'user_id': 101234036, 'first_name': 'Mega',       'last_name': 'Putri',        'username': None,              'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(days=8, hours=6)).isoformat()},
        {'id': 37, 'user_id': 101234037, 'first_name': 'Teguh',      'last_name': 'Prasetyo',     'username': 'teguh_prs',       'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(days=9)).isoformat()},
        {'id': 38, 'user_id': 101234038, 'first_name': 'Wulan',      'last_name': 'Sari',         'username': 'wulan_sri',       'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(days=9, hours=3)).isoformat()},
        {'id': 39, 'user_id': 101234039, 'first_name': 'Rendi',      'last_name': 'Pratama',      'username': None,              'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(days=10)).isoformat()},
        {'id': 40, 'user_id': 101234040, 'first_name': 'Annisa',     'last_name': 'Fajriani',     'username': 'annisa_fj',       'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(days=10, hours=8)).isoformat()},
        {'id': 41, 'user_id': 101234041, 'first_name': 'Pradipta',   'last_name': 'Kusuma',       'username': 'pradipta_k',      'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(days=11)).isoformat()},
        {'id': 42, 'user_id': 101234042, 'first_name': 'Eka',        'last_name': 'Wardani',      'username': None,              'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(days=12)).isoformat()},
        {'id': 43, 'user_id': 101234043, 'first_name': 'Wahyudi',    'last_name': 'Nugroho',      'username': 'wahyudi_n',       'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(days=13)).isoformat()},
        {'id': 44, 'user_id': 101234044, 'first_name': 'Rara',       'last_name': 'Indriani',     'username': 'rara_ind',        'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(days=14)).isoformat()},
        {'id': 45, 'user_id': 101234045, 'first_name': 'Sugeng',     'last_name': 'Raharjo',      'username': None,              'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(days=15)).isoformat()},
        {'id': 46, 'user_id': 101234046, 'first_name': 'Kartika',    'last_name': 'Sari',         'username': 'kartika_s',       'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(days=16)).isoformat()},
        {'id': 47, 'user_id': 101234047, 'first_name': 'Pandu',      'last_name': 'Wicaksono',    'username': 'pandu_wck',       'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(days=17)).isoformat()},
        {'id': 48, 'user_id': 101234048, 'first_name': 'Tika',       'last_name': 'Fitriani',     'username': None,              'phone': None, 'source_phone': '+6281298765432', 'last_interaction': (now - timedelta(days=18)).isoformat()},
        {'id': 49, 'user_id': 101234049, 'first_name': 'Surya',      'last_name': 'Hadiwibowo',   'username': 'surya_hw',        'phone': None, 'source_phone': '+6281234567890', 'last_interaction': (now - timedelta(days=19)).isoformat()},
        {'id': 50, 'user_id': 101234050, 'first_name': 'Melati',     'last_name': 'Kusumawardani','username': 'melati_kw',       'phone': None, 'source_phone': '+6285612349876', 'last_interaction': (now - timedelta(days=20)).isoformat()},
    ]


def get_local_keywords():
    now = _now()
    return [
        {'id': 1,  'keyword': 'harga',    'response': 'Harga produk kami mulai dari Rp 50.000 – Rp 500.000 tergantung jenis produk. Silakan DM kami untuk info harga lengkap ya! 😊', 'target_phone': 'all', 'user_id': 'local-user', 'created_at': (now - timedelta(days=30)).isoformat()},
        {'id': 2,  'keyword': 'order',    'response': 'Untuk order silahkan klik link di bio atau ketik nama produk yang kamu mau ya! Kami siap melayani 24 jam. 🛒', 'target_phone': 'all', 'user_id': 'local-user', 'created_at': (now - timedelta(days=28)).isoformat()},
        {'id': 3,  'keyword': 'promo',    'response': '🎉 Promo aktif sekarang:\n✅ Diskon 50% semua produk pilihan\n✅ Gratis ongkir min. 100rb\n✅ Berlaku hari ini saja!\n\nJangan lewatkan ya!', 'target_phone': 'all', 'user_id': 'local-user', 'created_at': (now - timedelta(days=25)).isoformat()},
        {'id': 4,  'keyword': 'stok',     'response': 'Stok semua produk masih tersedia ya kak! Untuk info stok terkini silakan DM langsung atau cek katalog di bio kami. 📦', 'target_phone': 'all', 'user_id': 'local-user', 'created_at': (now - timedelta(days=20)).isoformat()},
        {'id': 5,  'keyword': 'ongkir',   'response': 'Ongkos kirim bervariasi tergantung lokasi:\n📍 Jabodetabek: Rp 10.000\n📍 Pulau Jawa: Rp 15.000\n📍 Luar Jawa: Rp 25.000\n\nGratis ongkir untuk pembelian min. Rp 100.000! 🚀', 'target_phone': 'all', 'user_id': 'local-user', 'created_at': (now - timedelta(days=18)).isoformat()},
        {'id': 6,  'keyword': 'garansi',  'response': 'Produk kami bergaransi resmi 1 tahun! 🛡️\nJika ada kendala dalam masa garansi, cukup hubungi CS kami dan kami akan bantu proses klaimnya. Tenang aja ya kak!', 'target_phone': 'all', 'user_id': 'local-user', 'created_at': (now - timedelta(days=15)).isoformat()},
        {'id': 7,  'keyword': 'payment',  'response': 'Metode pembayaran yang kami terima:\n💳 Transfer Bank (BCA, Mandiri, BNI, BRI)\n📱 GoPay, OVO, DANA, ShopeePay\n💵 COD (area tertentu)\n\nSemua transaksi aman & terjamin! ✅', 'target_phone': 'all', 'user_id': 'local-user', 'created_at': (now - timedelta(days=12)).isoformat()},
        {'id': 8,  'keyword': 'alamat',   'response': '📍 Alamat toko kami:\nJl. Sudirman No. 123, Jakarta Pusat\n\n🕐 Jam operasional:\nSenin–Sabtu: 09.00–21.00 WIB\nMinggu: 10.00–18.00 WIB\n\nKunjungi kami atau order via online ya! 😊', 'target_phone': 'all', 'user_id': 'local-user', 'created_at': (now - timedelta(days=10)).isoformat()},
        {'id': 9,  'keyword': 'retur',    'response': 'Kebijakan retur kami:\n✅ Retur dalam 7 hari sejak barang diterima\n✅ Barang harus dalam kondisi original\n✅ Sertakan foto bukti kerusakan\n\nHubungi CS kami untuk proses retur lebih lanjut. 📞', 'target_phone': 'all', 'user_id': 'local-user', 'created_at': (now - timedelta(days=8)).isoformat()},
        {'id': 10, 'keyword': 'grosir',   'response': '🏭 Program Grosir & Reseller:\n• Min. order 10 pcs → Diskon 15%\n• Min. order 25 pcs → Diskon 25%\n• Min. order 50 pcs → Diskon 35%\n\nDaftar sebagai reseller kami sekarang dan dapatkan keuntungan lebih besar! 💰', 'target_phone': 'all', 'user_id': 'local-user', 'created_at': (now - timedelta(days=5)).isoformat()},
        {'id': 11, 'keyword': 'cs',       'response': 'Tim CS kami siap melayani 24 jam:\n📞 WhatsApp: +62812-3456-7890\n📧 Email: cs@tokokami.com\n💬 Telegram: @cstokokami\n\nRespon rata-rata < 5 menit. Hubungi kami sekarang! 🙋', 'target_phone': 'all', 'user_id': 'local-user', 'created_at': (now - timedelta(days=3)).isoformat()},
        {'id': 12, 'keyword': 'katalog',  'response': '📚 Katalog produk lengkap kami:\n🌐 Website: www.tokokami.com\n📷 Instagram: @tokokami_official\n📘 Facebook: Toko Kami Indonesia\n\nFollow akun kami untuk update produk & promo terbaru! ✨', 'target_phone': 'all', 'user_id': 'local-user', 'created_at': (now - timedelta(days=1)).isoformat()},
    ]


def get_local_auto_reply_settings():
    return {
        'is_active': True,
        'cooldown_minutes': 60,
        'welcome_message': 'Halo kak! 👋 Terima kasih sudah menghubungi kami. Ada yang bisa kami bantu?\n\nKetik salah satu keyword berikut untuk info lebih lanjut:\n- *harga* – Info harga produk\n- *order* – Cara pemesanan\n- *promo* – Promo aktif\n- *stok* – Cek stok produk\n- *ongkir* – Info ongkos kirim\n- *garansi* – Info garansi produk\n- *payment* – Metode pembayaran\n- *cs* – Hubungi customer service',
        'target_phone': 'all',
        'user_id': 'local-user'
    }


def get_local_blast_logs():
    now = _now()

    entries = [
        # Hari ini
        ('Grup Jual Beli Jakarta',           '-1001234567001', 'SUCCESS', None,                              now - timedelta(minutes=5),    '+6281234567890'),
        ('FJB Bandung Official',             '-1001234567002', 'SUCCESS', None,                              now - timedelta(minutes=13),   '+6281234567890'),
        ('Info Loker Surabaya',              '-1001234567003', 'SUCCESS', None,                              now - timedelta(minutes=21),   '+6281298765432'),
        ('Komunitas UMKM Yogyakarta',        '-1001234567004', 'FAILED',  'FloodWait 30 detik dari Telegram',now - timedelta(minutes=30),   '+6281234567890'),
        ('Toko Online Semarang',             '-1001234567005', 'SUCCESS', None,                              now - timedelta(minutes=40),   '+6281298765432'),
        ('FJB Depok & Bekasi',               '-1001234567050', 'SUCCESS', None,                              now - timedelta(minutes=52),   '+6285612349876'),
        ('Jual Beli Bogor Raya',             '-1001234567051', 'SUCCESS', None,                              now - timedelta(hours=1),      '+6281234567890'),
        ('Olshop Tangerang Selatan',         '-1001234567052', 'SUCCESS', None,                              now - timedelta(hours=1, minutes=15), '+6281298765432'),
        ('Pedagang Pasar Baru Jakarta',      '-1001234567053', 'FAILED',  'Peer flood, coba lagi nanti',    now - timedelta(hours=1, minutes=30), '+6285612349876'),
        ('Komunitas Dropshipper Jakarta',    '-1001234567054', 'SUCCESS', None,                              now - timedelta(hours=2),      '+6281234567890'),
        # Kemarin
        ('Marketplace Medan Group',          '-1001234567006', 'SUCCESS', None,                              now - timedelta(hours=25),     '+6281298765432'),
        ('Pedagang Online Makassar',         '-1001234567007', 'SUCCESS', None,                              now - timedelta(hours=26),     '+6281234567890'),
        ('FJB Palembang Resmi',              '-1001234567008', 'SUCCESS', None,                              now - timedelta(hours=27),     '+6285612349876'),
        ('Komunitas Bisnis Balikpapan',      '-1001234567060', 'SUCCESS', None,                              now - timedelta(hours=28),     '+6281298765432'),
        ('Jualan Online Pontianak',          '-1001234567061', 'FAILED',  'UserDeactivated: akun target tidak aktif', now - timedelta(hours=29), '+6281234567890'),
        ('FJB Samarinda & Kukar',            '-1001234567062', 'SUCCESS', None,                              now - timedelta(hours=30),     '+6285612349876'),
        ('Reseller Nasional Aktif',          '-1001234567063', 'SUCCESS', None,                              now - timedelta(hours=31),     '+6281298765432'),
        ('Dropshipper Sulawesi Selatan',     '-1001234567064', 'SUCCESS', None,                              now - timedelta(hours=32),     '+6281234567890'),
        # 2 hari lalu
        ('Grup Flash Sale Indonesia',        '-1001234567070', 'SUCCESS', None,                              now - timedelta(days=2, hours=1),  '+6281234567890'),
        ('Promo Murah Jakarta Selatan',      '-1001234567071', 'SUCCESS', None,                              now - timedelta(days=2, hours=2),  '+6281298765432'),
        ('Diskon Hari Ini Surabaya',         '-1001234567072', 'SUCCESS', None,                              now - timedelta(days=2, hours=3),  '+6285612349876'),
        ('Jual Murah Bandung Raya',          '-1001234567073', 'FAILED',  'ChatForbidden: tidak bisa kirim ke grup ini', now - timedelta(days=2, hours=4), '+6281234567890'),
        ('Weekend Deal Yogyakarta',          '-1001234567074', 'SUCCESS', None,                              now - timedelta(days=2, hours=5),  '+6281298765432'),
        ('Sale Elektronik Semarang',         '-1001234567075', 'SUCCESS', None,                              now - timedelta(days=2, hours=6),  '+6281234567890'),
        # 3 hari lalu
        ('Reseller Baju Grosir Tanah Abang', '-1001234567080', 'SUCCESS', None,                             now - timedelta(days=3, hours=1),  '+6285612349876'),
        ('Dropship Tas & Sepatu',            '-1001234567081', 'SUCCESS', None,                              now - timedelta(days=3, hours=2),  '+6281298765432'),
        ('Agen Kosmetik Murah Bandung',      '-1001234567082', 'SUCCESS', None,                              now - timedelta(days=3, hours=3),  '+6285612349876'),
        ('Distributor Sembako Nasional',     '-1001234567083', 'FAILED',  'SlowModeWait: grup aktifkan slow mode', now - timedelta(days=3, hours=4), '+6281298765432'),
        ('Supplier Elektronik Surabaya',     '-1001234567084', 'SUCCESS', None,                              now - timedelta(days=3, hours=5),  '+6285612349876'),
        ('Grosir Fashion Muslim Jakarta',    '-1001234567085', 'SUCCESS', None,                              now - timedelta(days=3, hours=6),  '+6281234567890'),
        # 5 hari lalu
        ('Komunitas Startup Jaksel',         '-1001234567090', 'SUCCESS', None,                              now - timedelta(days=5, hours=1),  '+6281234567890'),
        ('Tech & Gadget Indonesia',          '-1001234567091', 'SUCCESS', None,                              now - timedelta(days=5, hours=2),  '+6281298765432'),
        ('Penggemar Produk Lokal',           '-1001234567092', 'SUCCESS', None,                              now - timedelta(days=5, hours=3),  '+6285612349876'),
        ('UMKM Digital Nusantara',           '-1001234567093', 'FAILED',  'FloodWait 120 detik dari Telegram', now - timedelta(days=5, hours=4), '+6281234567890'),
        ('Wirausaha Muda Indonesia',         '-1001234567094', 'SUCCESS', None,                              now - timedelta(days=5, hours=5),  '+6281298765432'),
        # 7 hari lalu
        ('Bazaar Ramadhan Jakarta',          '-1001234567100', 'SUCCESS', None,                              now - timedelta(days=7, hours=1),  '+6281298765432'),
        ('Baju Muslim Grosir Surabaya',      '-1001234567101', 'SUCCESS', None,                              now - timedelta(days=7, hours=2),  '+6281234567890'),
        ('Hampers Lebaran Murah',            '-1001234567102', 'SUCCESS', None,                              now - timedelta(days=7, hours=3),  '+6285612349876'),
        ('Jualan Online Ramadhan Sale',      '-1001234567103', 'SUCCESS', None,                              now - timedelta(days=7, hours=4),  '+6281298765432'),
        ('Promo Sahur & Buka Puasa',         '-1001234567104', 'FAILED',  'ChatAdminRequired: perlu hak admin', now - timedelta(days=7, hours=5), '+6281234567890'),
        ('Takjil & Kue Lebaran Murah',       '-1001234567105', 'SUCCESS', None,                              now - timedelta(days=7, hours=6),  '+6285612349876'),
        # 10 hari lalu
        ('Belanja Hemat Malang',             '-1001234567110', 'SUCCESS', None,                              now - timedelta(days=10, hours=1), '+6285612349876'),
        ('Promo Akhir Bulan Surabaya',       '-1001234567111', 'SUCCESS', None,                              now - timedelta(days=10, hours=2), '+6281234567890'),
        ('Sale Besar Tangerang',             '-1001234567112', 'SUCCESS', None,                              now - timedelta(days=10, hours=3), '+6281298765432'),
        ('Cashback Gede Bekasi',             '-1001234567113', 'FAILED',  'MessageIdInvalid: pesan tidak ditemukan', now - timedelta(days=10, hours=4), '+6285612349876'),
        ('Komunitas Pembeli Cerdas',         '-1001234567120', 'SUCCESS', None,                              now - timedelta(days=10, hours=5), '+6281234567890'),
        # 14 hari lalu
        ('Review Produk Indonesia',          '-1001234567121', 'SUCCESS', None,                              now - timedelta(days=14, hours=1), '+6281298765432'),
        ('Testimoni Pelanggan Setia',        '-1001234567122', 'SUCCESS', None,                              now - timedelta(days=14, hours=2), '+6285612349876'),
        ('Member VIP Toko Kami',             '-1001234567130', 'SUCCESS', None,                              now - timedelta(days=14, hours=3), '+6281298765432'),
        ('Pelanggan Loyal Batch 1',          '-1001234567131', 'SUCCESS', None,                              now - timedelta(days=14, hours=4), '+6281234567890'),
    ]

    logs = []
    for i, (grp, gid, status, err, ts, phone) in enumerate(entries):
        wib = ts
        logs.append({
            'id': i + 1,
            'group_name': grp,
            'group_id': gid,
            'status': status,
            'error_message': err,
            'sender_phone': phone,
            'created_at': ts.isoformat(),
            'wib_time': wib.strftime('%H:%M:%S'),
            'wib_date': wib.strftime('%Y-%m-%d'),
            'user_id': 'local-user'
        })
    return logs


def get_local_stats():
    logs = get_local_blast_logs()
    success = sum(1 for l in logs if l['status'] == 'SUCCESS')
    total = len(logs)
    return {
        'connected_accounts': 3,
        'total_blast': total,
        'success_rate': int((success / total) * 100) if total > 0 else 0,
        'active_schedules': 6
    }


def get_local_plans():
    starter_features = [
        '2 Akun Telegram Aktif',
        '500 Grup Target',
        'Blast Pesan Teks',
        'Jadwal Blast Otomatis',
        'Auto-Reply Keyword',
        'CRM Pelanggan Dasar',
        'Laporan Statistik',
    ]
    pro_features = [
        '5 Akun Telegram Aktif',
        '2.000 Grup Target',
        'Blast Teks + Foto/Media',
        'Jadwal Blast Otomatis',
        'Auto-Reply Keyword',
        'CRM Pelanggan Lengkap',
        'Dukungan via WhatsApp',
        'Statistik & Analitik Detail',
    ]
    agency_features = [
        'Unlimited Akun Telegram',
        'Unlimited Grup Target',
        'Blast Teks + Foto/Media',
        'Multi-User Dashboard',
        'Jadwal Blast Otomatis',
        'Auto-Reply Keyword',
        'CRM Pelanggan Lengkap',
        'Prioritas Dukungan 24/7',
        'Laporan & Analitik Lanjutan',
    ]

    return {
        'basic': [
            {
                'id': 101, 'title': 'Bulanan', 'duration': '30 Hari',
                'price': 'Rp 150.000', 'rawPrice': 150000,
                'coret': 'Rp 250.000', 'hemat': 'Hemat 100Rb',
                'features': starter_features, 'btnText': 'Pilih Paket', 'bestValue': False,
            },
            {
                'id': 102, 'title': 'Quarterly', 'duration': '90 Hari',
                'price': 'Rp 390.000', 'rawPrice': 390000,
                'coret': 'Rp 600.000', 'hemat': 'Hemat 210Rb',
                'features': starter_features, 'btnText': 'Pilih Paket', 'bestValue': True,
            },
            {
                'id': 103, 'title': 'Semester', 'duration': '180 Hari',
                'price': 'Rp 690.000', 'rawPrice': 690000,
                'coret': 'Rp 1.050.000', 'hemat': 'Hemat 360Rb',
                'features': starter_features, 'btnText': 'Pilih Paket', 'bestValue': False,
            },
        ],
        'optimal': [
            {
                'id': 201, 'title': 'Bulanan', 'duration': '30 Hari',
                'price': 'Rp 250.000', 'rawPrice': 250000,
                'coret': 'Rp 450.000', 'hemat': 'Hemat 200Rb',
                'features': pro_features, 'btnText': 'Pilih Paket', 'bestValue': False,
            },
            {
                'id': 202, 'title': 'Quarterly', 'duration': '90 Hari',
                'price': 'Rp 650.000', 'rawPrice': 650000,
                'coret': 'Rp 1.000.000', 'hemat': 'Hemat 350Rb',
                'features': pro_features, 'btnText': 'Pilih Paket', 'bestValue': True,
            },
            {
                'id': 203, 'title': 'Semester', 'duration': '180 Hari',
                'price': 'Rp 1.150.000', 'rawPrice': 1150000,
                'coret': 'Rp 1.800.000', 'hemat': 'Hemat 650Rb',
                'features': pro_features, 'btnText': 'Pilih Paket', 'bestValue': False,
            },
        ],
        'agency': [
            {
                'id': 301, 'title': 'Bulanan', 'duration': '30 Hari',
                'price': 'Rp 500.000', 'rawPrice': 500000,
                'coret': 'Rp 800.000', 'hemat': 'Hemat 300Rb',
                'features': agency_features, 'btnText': 'Pilih Paket', 'bestValue': False,
            },
            {
                'id': 302, 'title': 'Quarterly', 'duration': '90 Hari',
                'price': 'Rp 1.350.000', 'rawPrice': 1350000,
                'coret': 'Rp 2.100.000', 'hemat': 'Hemat 750Rb',
                'features': agency_features, 'btnText': 'Pilih Paket', 'bestValue': True,
            },
            {
                'id': 303, 'title': 'Semester', 'duration': '180 Hari',
                'price': 'Rp 2.400.000', 'rawPrice': 2400000,
                'coret': 'Rp 3.600.000', 'hemat': 'Hemat 1.2 Juta',
                'features': agency_features, 'btnText': 'Pilih Paket', 'bestValue': False,
            },
        ],
    }


def get_local_banks():
    return [
        {
            'id': 1,
            'bank_name': 'BCA',
            'account_number': '1234567890',
            'account_holder': 'PT BlastPro Indonesia',
            'is_active': True,
        },
        {
            'id': 2,
            'bank_name': 'Mandiri',
            'account_number': '9876543210',
            'account_holder': 'PT BlastPro Indonesia',
            'is_active': True,
        },
        {
            'id': 3,
            'bank_name': 'BNI',
            'account_number': '5544332211',
            'account_holder': 'PT BlastPro Indonesia',
            'is_active': True,
        },
        {
            'id': 4,
            'bank_name': 'GoPay / OVO / DANA',
            'account_number': '+6281234567890',
            'account_holder': 'BlastPro Official',
            'is_active': True,
        },
    ]

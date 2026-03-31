"""
Script untuk memasukkan data contoh ke Supabase untuk user demo.
Jalankan: python3 seed_demo.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta, timezone
from extensions import supabase

UID = 'd4d2e5af-92e7-46c9-aca3-b1509065f4d7'

def _ts(delta):
    return (datetime.now(timezone.utc) - delta).strftime('%Y-%m-%dT%H:%M:%S')

def clear_old_data():
    print("Membersihkan data lama...")
    for table, col in [
        ('blast_logs', 'user_id'), ('blast_schedules', 'user_id'),
        ('blast_targets', 'user_id'), ('keyword_rules', 'user_id'),
        ('auto_reply_settings', 'user_id'), ('message_templates', 'user_id'),
        ('telegram_accounts', 'user_id'), ('transactions', 'user_id'),
        ('notifications', 'user_id')
    ]:
        try:
            supabase.table(table).delete().eq(col, UID).execute()
        except:
            pass
    try:
        supabase.table('tele_users').delete().eq('owner_id', UID).execute()
    except:
        pass
    print("   Data lama berhasil dibersihkan")

def seed_telegram_accounts():
    print("Seeding telegram_accounts...")
    accounts = [
        {'user_id': UID, 'phone_number': '+6281234567890', 'first_name': 'Budi Santoso',
         'is_active': True, 'session_string': None, 'created_at': _ts(timedelta(days=30))},
        {'user_id': UID, 'phone_number': '+6281298765432', 'first_name': 'Toko Online',
         'is_active': True, 'session_string': None, 'created_at': _ts(timedelta(days=20))},
        {'user_id': UID, 'phone_number': '+6285612349876', 'first_name': 'Rina Widyaningsih',
         'is_active': True, 'session_string': None, 'created_at': _ts(timedelta(days=12))},
    ]
    res = supabase.table('telegram_accounts').insert(accounts).execute()
    print(f"   {len(res.data)} akun Telegram berhasil")
    return res.data

def seed_message_templates():
    print("Seeding message_templates...")
    templates = [
        {'user_id': UID, 'name': 'Promo Diskon 50%', 'created_at': _ts(timedelta(days=30)),
         'message_text': 'Halo {name}! Kabar gembira! Kami sedang mengadakan PROMO BESAR-BESARAN diskon hingga 50% untuk semua produk pilihan.\n\nPromo berlaku hari ini saja! Stok terbatas. Gratis ongkir min. order 100rb\n\nSegera order sekarang sebelum kehabisan!'},
        {'user_id': UID, 'name': 'Restock Barang Baru', 'created_at': _ts(timedelta(days=25)),
         'message_text': 'Halo {name}! Stok barang favorit kamu sudah READY lagi nih!\n\nProduk baru sudah tersedia. Order via DM atau klik link di bio. Pengiriman same day untuk order sebelum jam 12 siang\n\nJangan sampai kehabisan lagi ya!'},
        {'user_id': UID, 'name': 'Ucapan Selamat Pagi', 'created_at': _ts(timedelta(days=20)),
         'message_text': 'Selamat pagi {name}! Semangat menjalani hari ini ya! Jangan lupa cek produk terbaru kami yang pastinya bermanfaat untuk kamu.\n\nTetap produktif & sehat!'},
        {'user_id': UID, 'name': 'Follow Up Order', 'created_at': _ts(timedelta(days=18)),
         'message_text': 'Halo {name}! Kami ingin memastikan pesanan Anda sudah diterima dengan baik.\n\nStatus: Terkirim. Jika puas, mohon berikan ulasan ya!\n\nAda yang bisa kami bantu? Hubungi CS kami 24/7.'},
        {'user_id': UID, 'name': 'Flash Sale Weekend', 'created_at': _ts(timedelta(days=15)),
         'message_text': 'Halo {name}! FLASH SALE WEEKEND sudah dimulai!\n\nDiskon 70% produk tertentu. Hanya 24 jam mulai hari ini! Bonus hadiah untuk pembelian pertama\n\nBuruan sebelum HABIS!'},
        {'user_id': UID, 'name': 'Promo Ramadhan', 'created_at': _ts(timedelta(days=12)),
         'message_text': 'Assalamualaikum {name}! Sambut Ramadhan dengan penawaran spesial dari kami!\n\nDiskon 40% semua produk. Hadiah gratis untuk pembelian di atas 500rb. Gratis ongkir ke seluruh Indonesia\n\nRaih keberkahan Ramadhan bersama kami!'},
        {'user_id': UID, 'name': 'Blast Mingguan', 'created_at': _ts(timedelta(days=10)),
         'message_text': 'Halo {name}! Update mingguan produk terbaik kami sudah tiba!\n\nProduk terlaris minggu ini:\n1. Item A - Rp 75.000\n2. Item B - Rp 120.000\n3. Item C - Rp 55.000\n\nChat kami untuk pemesanan. Terima kasih!'},
        {'user_id': UID, 'name': 'Update Stok Produk', 'created_at': _ts(timedelta(days=8)),
         'message_text': 'Halo {name}! Stok produk terbaru kami telah di-update!\n\nTersedia dalam berbagai pilihan warna. Ukuran S hingga XL tersedia. Bahan premium berkualitas tinggi\n\nSegera pesan sebelum kehabisan!'},
        {'user_id': UID, 'name': 'Iklan Produk Baru', 'created_at': _ts(timedelta(days=5)),
         'message_text': 'Halo {name}! Produk BARU kami resmi diluncurkan hari ini!\n\nFitur unggulan:\n- Kualitas premium terjangkau\n- Garansi 1 tahun\n- Support purna jual 24/7\n\nJadi yang PERTAMA memilikinya! DM kami sekarang!'},
        {'user_id': UID, 'name': 'Testimoni & Review', 'created_at': _ts(timedelta(days=3)),
         'message_text': 'Halo {name}! "Produknya luar biasa! Kualitas premium, pengiriman cepat, CS sangat responsif. Pasti repeat order!" - Pelanggan setia\n\nDapatkan produk terbaik kami sekarang!'},
        {'user_id': UID, 'name': 'Akhir Bulan Promo', 'created_at': _ts(timedelta(hours=12)),
         'message_text': 'Halo {name}! PROGRAM AKHIR BULAN spesial untuk kamu!\n\nBelanja min 200rb - Cashback 20rb\nBelanja min 500rb - Cashback 75rb\nBelanja min 1jt - Cashback 200rb\n\nPromo hanya berlaku s.d. akhir bulan ini!'},
    ]
    res = supabase.table('message_templates').insert(templates).execute()
    print(f"   {len(res.data)} template berhasil")
    return res.data

def seed_blast_targets():
    print("Seeding blast_targets...")
    data = [
        ('Grup Jual Beli Jakarta', '-1001234567001', None, 'Promo Harian', '+6281234567890', 'Budi Santoso', timedelta(days=30)),
        ('FJB Bandung Official', '-1001234567002', '1,5', 'Promo Harian', '+6281234567890', 'Budi Santoso', timedelta(days=29)),
        ('Info Loker Surabaya', '-1001234567003', '1,8', 'Promo Harian', '+6281234567890', 'Budi Santoso', timedelta(days=28)),
        ('Komunitas UMKM Yogyakarta', '-1001234567004', None, 'Promo Harian', '+6281234567890', 'Budi Santoso', timedelta(days=27)),
        ('Toko Online Semarang', '-1001234567005', '1,3', 'Promo Harian', '+6281234567890', 'Budi Santoso', timedelta(days=26)),
        ('FJB Depok & Bekasi', '-1001234567050', '2,4', 'Promo Harian', '+6281234567890', 'Budi Santoso', timedelta(days=25)),
        ('Jual Beli Bogor Raya', '-1001234567051', None, 'Promo Harian', '+6281234567890', 'Budi Santoso', timedelta(days=24)),
        ('Olshop Tangerang Selatan', '-1001234567052', None, 'Promo Harian', '+6281234567890', 'Budi Santoso', timedelta(days=23)),
        ('Pedagang Pasar Baru Jakarta', '-1001234567053', '2,3', 'Promo Harian', '+6281234567890', 'Budi Santoso', timedelta(days=22)),
        ('Komunitas Dropshipper Jakarta', '-1001234567054', None, 'Promo Harian', '+6281234567890', 'Budi Santoso', timedelta(days=21)),
        ('Marketplace Medan Group', '-1001234567006', None, 'Blast Mingguan', '+6281298765432', 'Toko Online', timedelta(days=20)),
        ('Pedagang Online Makassar', '-1001234567007', '1,2', 'Blast Mingguan', '+6281298765432', 'Toko Online', timedelta(days=19)),
        ('FJB Palembang Resmi', '-1001234567008', None, 'Blast Mingguan', '+6281298765432', 'Toko Online', timedelta(days=18)),
        ('Komunitas Bisnis Balikpapan', '-1001234567060', '1,3', 'Blast Mingguan', '+6281298765432', 'Toko Online', timedelta(days=17)),
        ('Jualan Online Pontianak', '-1001234567061', None, 'Blast Mingguan', '+6281298765432', 'Toko Online', timedelta(days=16)),
        ('FJB Samarinda & Kukar', '-1001234567062', '2,5', 'Blast Mingguan', '+6281298765432', 'Toko Online', timedelta(days=15)),
        ('Reseller Nasional Aktif', '-1001234567063', None, 'Blast Mingguan', '+6281298765432', 'Toko Online', timedelta(days=14)),
        ('Dropshipper Sulawesi Selatan', '-1001234567064', '1,4', 'Blast Mingguan', '+6281298765432', 'Toko Online', timedelta(days=13)),
        ('Grup Flash Sale Indonesia', '-1001234567070', None, 'Flash Sale Weekend', '+6281234567890', 'Budi Santoso', timedelta(days=13)),
        ('Promo Murah Jakarta Selatan', '-1001234567071', '1,6', 'Flash Sale Weekend', '+6281234567890', 'Budi Santoso', timedelta(days=12)),
        ('Diskon Hari Ini Surabaya', '-1001234567072', '1,4', 'Flash Sale Weekend', '+6281234567890', 'Budi Santoso', timedelta(days=11)),
        ('Jual Murah Bandung Raya', '-1001234567073', None, 'Flash Sale Weekend', '+6281234567890', 'Budi Santoso', timedelta(days=10)),
        ('Weekend Deal Yogyakarta', '-1001234567074', None, 'Flash Sale Weekend', '+6281234567890', 'Budi Santoso', timedelta(days=9)),
        ('Sale Elektronik Semarang', '-1001234567075', '3,7', 'Flash Sale Weekend', '+6281234567890', 'Budi Santoso', timedelta(days=8)),
        ('Reseller Baju Grosir Tanah Abang', '-1001234567080', None, 'Update Stok Produk', '+6285612349876', 'Rina Widyaningsih', timedelta(days=8)),
        ('Dropship Tas & Sepatu', '-1001234567081', '1,2', 'Update Stok Produk', '+6285612349876', 'Rina Widyaningsih', timedelta(days=7)),
        ('Agen Kosmetik Murah Bandung', '-1001234567082', None, 'Update Stok Produk', '+6285612349876', 'Rina Widyaningsih', timedelta(days=6)),
        ('Distributor Sembako Nasional', '-1001234567083', '2,3', 'Update Stok Produk', '+6285612349876', 'Rina Widyaningsih', timedelta(days=5)),
        ('Supplier Elektronik Surabaya', '-1001234567084', None, 'Update Stok Produk', '+6285612349876', 'Rina Widyaningsih', timedelta(days=5)),
        ('Grosir Fashion Muslim Jakarta', '-1001234567085', '1,5', 'Update Stok Produk', '+6285612349876', 'Rina Widyaningsih', timedelta(days=4)),
        ('Komunitas Startup Jaksel', '-1001234567090', None, 'Iklan Produk Baru', '+6281234567890', 'Budi Santoso', timedelta(days=4)),
        ('Tech & Gadget Indonesia', '-1001234567091', '1,5', 'Iklan Produk Baru', '+6281234567890', 'Budi Santoso', timedelta(days=3)),
        ('Penggemar Produk Lokal', '-1001234567092', None, 'Iklan Produk Baru', '+6281234567890', 'Budi Santoso', timedelta(days=3)),
        ('UMKM Digital Nusantara', '-1001234567093', '2,6', 'Iklan Produk Baru', '+6281234567890', 'Budi Santoso', timedelta(days=2)),
        ('Wirausaha Muda Indonesia', '-1001234567094', None, 'Iklan Produk Baru', '+6281234567890', 'Budi Santoso', timedelta(days=2)),
        ('Bazaar Ramadhan Jakarta', '-1001234567100', None, 'Promo Ramadhan', '+6281298765432', 'Toko Online', timedelta(days=2)),
        ('Baju Muslim Grosir Surabaya', '-1001234567101', '1,3', 'Promo Ramadhan', '+6281298765432', 'Toko Online', timedelta(days=2)),
        ('Hampers Lebaran Murah', '-1001234567102', None, 'Promo Ramadhan', '+6281298765432', 'Toko Online', timedelta(days=1)),
        ('Jualan Online Ramadhan Sale', '-1001234567103', '2,4', 'Promo Ramadhan', '+6281298765432', 'Toko Online', timedelta(days=1)),
        ('Promo Sahur & Buka Puasa', '-1001234567104', None, 'Promo Ramadhan', '+6281298765432', 'Toko Online', timedelta(days=1)),
        ('Takjil & Kue Lebaran Murah', '-1001234567105', '1,2', 'Promo Ramadhan', '+6281298765432', 'Toko Online', timedelta(days=1)),
        ('Belanja Hemat Malang', '-1001234567110', None, 'Akhir Bulan Promo', '+6285612349876', 'Rina Widyaningsih', timedelta(hours=15)),
        ('Promo Akhir Bulan Surabaya', '-1001234567111', '3,5', 'Akhir Bulan Promo', '+6285612349876', 'Rina Widyaningsih', timedelta(hours=14)),
        ('Sale Besar Tangerang', '-1001234567112', None, 'Akhir Bulan Promo', '+6285612349876', 'Rina Widyaningsih', timedelta(hours=13)),
        ('Cashback Gede Bekasi', '-1001234567113', '1,4', 'Akhir Bulan Promo', '+6285612349876', 'Rina Widyaningsih', timedelta(hours=12)),
        ('Komunitas Pembeli Cerdas', '-1001234567120', None, 'Testimoni & Review', '+6281234567890', 'Budi Santoso', timedelta(hours=10)),
        ('Review Produk Indonesia', '-1001234567121', '2,3', 'Testimoni & Review', '+6281234567890', 'Budi Santoso', timedelta(hours=8)),
        ('Member VIP Toko Kami', '-1001234567130', None, 'Ucapan Selamat Pagi', '+6281298765432', 'Toko Online', timedelta(hours=6)),
        ('Pelanggan Loyal Batch 1', '-1001234567131', '1,2', 'Ucapan Selamat Pagi', '+6281298765432', 'Toko Online', timedelta(hours=4)),
        ('Komunitas Reseller Premium', '-1001234567140', None, 'Flash Sale Weekend', '+6281234567890', 'Budi Santoso', timedelta(hours=2)),
    ]

    targets = [{
        'user_id': UID, 'group_name': gn, 'group_id': gi,
        'topic_ids': ti, 'template_name': tmpl,
        'source_phone': phone, 'source_name': sname,
        'created_at': _ts(delta)
    } for (gn, gi, ti, tmpl, phone, sname, delta) in data]

    for i in range(0, len(targets), 20):
        res = supabase.table('blast_targets').insert(targets[i:i+20]).execute()
        print(f"   Batch {i//20+1}: {len(res.data)} targets")

def seed_blast_schedules(templates_data):
    print("Seeding blast_schedules...")
    tmpl_map = {t['name']: t['id'] for t in templates_data}

    schedules = [
        {'user_id': UID, 'run_hour': 7, 'run_minute': 0, 'is_active': True,
         'template_id': tmpl_map.get('Ucapan Selamat Pagi'), 'sender_phone': 'auto', 'target_template_name': 'Promo Harian'},
        {'user_id': UID, 'run_hour': 9, 'run_minute': 30, 'is_active': True,
         'template_id': tmpl_map.get('Promo Diskon 50%'), 'sender_phone': '+6281234567890', 'target_template_name': 'Promo Harian'},
        {'user_id': UID, 'run_hour': 12, 'run_minute': 0, 'is_active': True,
         'template_id': tmpl_map.get('Blast Mingguan'), 'sender_phone': '+6281298765432', 'target_template_name': 'Blast Mingguan'},
        {'user_id': UID, 'run_hour': 14, 'run_minute': 0, 'is_active': True,
         'template_id': tmpl_map.get('Flash Sale Weekend'), 'sender_phone': 'auto', 'target_template_name': 'Flash Sale Weekend'},
        {'user_id': UID, 'run_hour': 16, 'run_minute': 30, 'is_active': True,
         'template_id': tmpl_map.get('Restock Barang Baru'), 'sender_phone': '+6285612349876', 'target_template_name': 'Update Stok Produk'},
        {'user_id': UID, 'run_hour': 19, 'run_minute': 0, 'is_active': True,
         'template_id': tmpl_map.get('Iklan Produk Baru'), 'sender_phone': '+6281234567890', 'target_template_name': 'Iklan Produk Baru'},
        {'user_id': UID, 'run_hour': 20, 'run_minute': 0, 'is_active': False,
         'template_id': tmpl_map.get('Follow Up Order'), 'sender_phone': '+6281298765432', 'target_template_name': None},
        {'user_id': UID, 'run_hour': 21, 'run_minute': 30, 'is_active': False,
         'template_id': tmpl_map.get('Akhir Bulan Promo'), 'sender_phone': 'auto', 'target_template_name': 'Akhir Bulan Promo'},
    ]
    res = supabase.table('blast_schedules').insert(schedules).execute()
    print(f"   {len(res.data)} jadwal berhasil")

def seed_blast_logs():
    print("Seeding blast_logs...")
    entries = [
        ('Grup Jual Beli Jakarta', '-1001234567001', 'SUCCESS', None, timedelta(minutes=5)),
        ('FJB Bandung Official', '-1001234567002', 'SUCCESS', None, timedelta(minutes=13)),
        ('Info Loker Surabaya', '-1001234567003', 'SUCCESS', None, timedelta(minutes=21)),
        ('Komunitas UMKM Yogyakarta', '-1001234567004', 'FAILED', 'FloodWait 30 detik dari Telegram', timedelta(minutes=30)),
        ('Toko Online Semarang', '-1001234567005', 'SUCCESS', None, timedelta(minutes=40)),
        ('FJB Depok & Bekasi', '-1001234567050', 'SUCCESS', None, timedelta(hours=1)),
        ('Jual Beli Bogor Raya', '-1001234567051', 'SUCCESS', None, timedelta(hours=1, minutes=15)),
        ('Olshop Tangerang Selatan', '-1001234567052', 'SUCCESS', None, timedelta(hours=1, minutes=30)),
        ('Pedagang Pasar Baru Jakarta', '-1001234567053', 'FAILED', 'Peer flood, coba lagi nanti', timedelta(hours=1, minutes=45)),
        ('Komunitas Dropshipper Jakarta', '-1001234567054', 'SUCCESS', None, timedelta(hours=2)),
        ('Marketplace Medan Group', '-1001234567006', 'SUCCESS', None, timedelta(hours=25)),
        ('Pedagang Online Makassar', '-1001234567007', 'SUCCESS', None, timedelta(hours=26)),
        ('FJB Palembang Resmi', '-1001234567008', 'SUCCESS', None, timedelta(hours=27)),
        ('Komunitas Bisnis Balikpapan', '-1001234567060', 'SUCCESS', None, timedelta(hours=28)),
        ('Jualan Online Pontianak', '-1001234567061', 'FAILED', 'UserDeactivated: akun target tidak aktif', timedelta(hours=29)),
        ('FJB Samarinda & Kukar', '-1001234567062', 'SUCCESS', None, timedelta(hours=30)),
        ('Reseller Nasional Aktif', '-1001234567063', 'SUCCESS', None, timedelta(hours=31)),
        ('Dropshipper Sulawesi Selatan', '-1001234567064', 'SUCCESS', None, timedelta(hours=32)),
        ('Grup Flash Sale Indonesia', '-1001234567070', 'SUCCESS', None, timedelta(days=2, hours=1)),
        ('Promo Murah Jakarta Selatan', '-1001234567071', 'SUCCESS', None, timedelta(days=2, hours=2)),
        ('Diskon Hari Ini Surabaya', '-1001234567072', 'SUCCESS', None, timedelta(days=2, hours=3)),
        ('Jual Murah Bandung Raya', '-1001234567073', 'FAILED', 'ChatForbidden: tidak bisa kirim ke grup ini', timedelta(days=2, hours=4)),
        ('Weekend Deal Yogyakarta', '-1001234567074', 'SUCCESS', None, timedelta(days=2, hours=5)),
        ('Sale Elektronik Semarang', '-1001234567075', 'SUCCESS', None, timedelta(days=2, hours=6)),
        ('Reseller Baju Grosir Tanah Abang', '-1001234567080', 'SUCCESS', None, timedelta(days=3, hours=1)),
        ('Dropship Tas & Sepatu', '-1001234567081', 'SUCCESS', None, timedelta(days=3, hours=2)),
        ('Agen Kosmetik Murah Bandung', '-1001234567082', 'SUCCESS', None, timedelta(days=3, hours=3)),
        ('Distributor Sembako Nasional', '-1001234567083', 'FAILED', 'SlowModeWait: grup aktifkan slow mode', timedelta(days=3, hours=4)),
        ('Supplier Elektronik Surabaya', '-1001234567084', 'SUCCESS', None, timedelta(days=3, hours=5)),
        ('Grosir Fashion Muslim Jakarta', '-1001234567085', 'SUCCESS', None, timedelta(days=3, hours=6)),
        ('Komunitas Startup Jaksel', '-1001234567090', 'SUCCESS', None, timedelta(days=5, hours=1)),
        ('Tech & Gadget Indonesia', '-1001234567091', 'SUCCESS', None, timedelta(days=5, hours=2)),
        ('Penggemar Produk Lokal', '-1001234567092', 'SUCCESS', None, timedelta(days=5, hours=3)),
        ('UMKM Digital Nusantara', '-1001234567093', 'FAILED', 'FloodWait 120 detik dari Telegram', timedelta(days=5, hours=4)),
        ('Wirausaha Muda Indonesia', '-1001234567094', 'SUCCESS', None, timedelta(days=5, hours=5)),
        ('Bazaar Ramadhan Jakarta', '-1001234567100', 'SUCCESS', None, timedelta(days=7, hours=1)),
        ('Baju Muslim Grosir Surabaya', '-1001234567101', 'SUCCESS', None, timedelta(days=7, hours=2)),
        ('Hampers Lebaran Murah', '-1001234567102', 'SUCCESS', None, timedelta(days=7, hours=3)),
        ('Jualan Online Ramadhan Sale', '-1001234567103', 'SUCCESS', None, timedelta(days=7, hours=4)),
        ('Promo Sahur & Buka Puasa', '-1001234567104', 'FAILED', 'ChatAdminRequired: perlu hak admin', timedelta(days=7, hours=5)),
        ('Takjil & Kue Lebaran Murah', '-1001234567105', 'SUCCESS', None, timedelta(days=7, hours=6)),
        ('Belanja Hemat Malang', '-1001234567110', 'SUCCESS', None, timedelta(days=10, hours=1)),
        ('Promo Akhir Bulan Surabaya', '-1001234567111', 'SUCCESS', None, timedelta(days=10, hours=2)),
        ('Sale Besar Tangerang', '-1001234567112', 'SUCCESS', None, timedelta(days=10, hours=3)),
        ('Cashback Gede Bekasi', '-1001234567113', 'FAILED', 'MessageIdInvalid: pesan tidak ditemukan', timedelta(days=10, hours=4)),
        ('Komunitas Pembeli Cerdas', '-1001234567120', 'SUCCESS', None, timedelta(days=10, hours=5)),
        ('Review Produk Indonesia', '-1001234567121', 'SUCCESS', None, timedelta(days=14, hours=1)),
        ('Testimoni Pelanggan Setia', '-1001234567122', 'SUCCESS', None, timedelta(days=14, hours=2)),
        ('Member VIP Toko Kami', '-1001234567130', 'SUCCESS', None, timedelta(days=14, hours=3)),
        ('Pelanggan Loyal Batch 1', '-1001234567131', 'SUCCESS', None, timedelta(days=14, hours=4)),
    ]

    logs = [{'user_id': UID, 'group_name': gn, 'group_id': gi,
              'status': st, 'error_message': err, 'created_at': _ts(delta)}
             for (gn, gi, st, err, delta) in entries]

    for i in range(0, len(logs), 20):
        res = supabase.table('blast_logs').insert(logs[i:i+20]).execute()
        print(f"   Batch {i//20+1}: {len(res.data)} logs")

def seed_crm_users():
    print("Seeding tele_users (CRM)...")
    contacts = [
        (101234001, 'Budi Santoso', 'budi_s99', '+6281234567890', timedelta(minutes=5)),
        (101234002, 'Siti Aminah', None, '+6281234567890', timedelta(hours=1)),
        (101234003, 'Doni Prasetyo', 'donipras', '+6281234567890', timedelta(hours=2)),
        (101234004, 'Rina Widyaningsih', 'rinawd_shop', '+6281234567890', timedelta(hours=3)),
        (101234005, 'Ahmad Fauzi', None, '+6281298765432', timedelta(hours=4)),
        (101234006, 'Dewi Lestari', 'dewilestari_id', '+6281298765432', timedelta(hours=5)),
        (101234007, 'Rizky Ramadan', 'rizky_rd', '+6281298765432', timedelta(hours=6)),
        (101234008, 'Nurul Hidayah', None, '+6281234567890', timedelta(hours=8)),
        (101234009, 'Eko Wahyudi', 'eko_ws', '+6281234567890', timedelta(hours=10)),
        (101234010, 'Fitri Handayani', 'fitrihandayani', '+6281298765432', timedelta(hours=12)),
        (101234011, 'Hendra Gunawan', 'hendra_gw', '+6281234567890', timedelta(hours=14)),
        (101234012, 'Yuliana Permata', None, '+6285612349876', timedelta(hours=16)),
        (101234013, 'Rudi Kurniawan', 'rudi_kurn', '+6281298765432', timedelta(hours=18)),
        (101234014, 'Maya Anggraeni', 'maya_angg', '+6281234567890', timedelta(hours=20)),
        (101234015, 'Fajar Nugroho', None, '+6285612349876', timedelta(hours=22)),
        (101234016, 'Indah Sari', 'indahsari_shop', '+6281298765432', timedelta(days=1)),
        (101234017, 'Bagas Pramudita', 'bagas_pram', '+6281234567890', timedelta(days=1, hours=3)),
        (101234018, 'Ayu Wulandari', None, '+6285612349876', timedelta(days=1, hours=6)),
        (101234019, 'Galih Setiawan', 'galih_set', '+6281298765432', timedelta(days=2)),
        (101234020, 'Putri Maharani', 'putri_mhr', '+6281234567890', timedelta(days=2, hours=4)),
        (101234021, 'Wahyu Pratama', None, '+6281298765432', timedelta(days=2, hours=8)),
        (101234022, 'Laras Kusumawati', 'laras_kw', '+6285612349876', timedelta(days=3)),
        (101234023, 'Dimas Aditya', 'dimas_adt', '+6281234567890', timedelta(days=3, hours=6)),
        (101234024, 'Novita Rahmawati', None, '+6281298765432', timedelta(days=4)),
        (101234025, 'Agus Hermawan', 'agus_hrm', '+6281234567890', timedelta(days=4, hours=5)),
        (101234026, 'Trisna Dewi', 'trisna_d', '+6285612349876', timedelta(days=5)),
        (101234027, 'Yudi Laksono', None, '+6281298765432', timedelta(days=5, hours=3)),
        (101234028, 'Nia Kusuma', 'nia_kus', '+6281234567890', timedelta(days=6)),
        (101234029, 'Hendro Wijayanto', 'hendro_wj', '+6285612349876', timedelta(days=6, hours=8)),
        (101234030, 'Sari Puspitasari', None, '+6281298765432', timedelta(days=7)),
        (101234031, 'Bambang Suryanto', 'bambang_sry', '+6281234567890', timedelta(days=7, hours=6)),
        (101234032, 'Lina Marlina', 'lina_mrl', '+6285612349876', timedelta(days=8)),
        (101234033, 'Kevin Wijaya', None, '+6281298765432', timedelta(days=8, hours=4)),
        (101234034, 'Suci Rahayu', 'suci_rhy', '+6281234567890', timedelta(days=9)),
        (101234035, 'Ferry Adriansyah', 'ferry_adn', '+6285612349876', timedelta(days=9, hours=8)),
        (101234036, 'Mega Putri', None, '+6281298765432', timedelta(days=10)),
        (101234037, 'Teguh Prasetyo', 'teguh_prs', '+6281234567890', timedelta(days=10, hours=6)),
        (101234038, 'Wulan Sari', 'wulan_sri', '+6285612349876', timedelta(days=11)),
        (101234039, 'Rendi Pratama', None, '+6281298765432', timedelta(days=12)),
        (101234040, 'Annisa Fajriani', 'annisa_fj', '+6281234567890', timedelta(days=12, hours=8)),
        (101234041, 'Pradipta Kusuma', 'pradipta_k', '+6285612349876', timedelta(days=13)),
        (101234042, 'Eka Wardani', None, '+6281298765432', timedelta(days=14)),
        (101234043, 'Wahyudi Nugroho', 'wahyudi_n', '+6281234567890', timedelta(days=15)),
        (101234044, 'Rara Indriani', 'rara_ind', '+6285612349876', timedelta(days=16)),
        (101234045, 'Sugeng Raharjo', None, '+6281298765432', timedelta(days=17)),
        (101234046, 'Kartika Sari', 'kartika_s', '+6281234567890', timedelta(days=18)),
        (101234047, 'Pandu Wicaksono', 'pandu_wck', '+6285612349876', timedelta(days=19)),
        (101234048, 'Tika Fitriani', None, '+6281298765432', timedelta(days=20)),
        (101234049, 'Surya Hadiwibowo', 'surya_hw', '+6281234567890', timedelta(days=21)),
        (101234050, 'Melati Kusumawardani', 'melati_kw', '+6285612349876', timedelta(days=22)),
    ]

    crm = [{'owner_id': UID, 'user_id': tid, 'first_name': fn,
             'username': uname, 'source_phone': phone,
             'last_interaction': _ts(delta)}
            for (tid, fn, uname, phone, delta) in contacts]

    for i in range(0, len(crm), 20):
        res = supabase.table('tele_users').insert(crm[i:i+20]).execute()
        print(f"   Batch {i//20+1}: {len(res.data)} CRM users")

def seed_keyword_rules():
    print("Seeding keyword_rules...")
    keywords = [
        {'user_id': UID, 'keyword': 'harga', 'target_phone': 'all', 'created_at': _ts(timedelta(days=30)),
         'response': 'Harga produk kami mulai dari Rp 50.000 sampai Rp 500.000 tergantung jenis produk. Silakan DM kami untuk info harga lengkap ya!'},
        {'user_id': UID, 'keyword': 'order', 'target_phone': 'all', 'created_at': _ts(timedelta(days=28)),
         'response': 'Untuk order silahkan klik link di bio atau ketik nama produk yang kamu mau ya! Kami siap melayani 24 jam.'},
        {'user_id': UID, 'keyword': 'promo', 'target_phone': 'all', 'created_at': _ts(timedelta(days=25)),
         'response': 'Promo aktif sekarang:\n- Diskon 50% semua produk pilihan\n- Gratis ongkir min. 100rb\n- Berlaku hari ini saja!\n\nJangan lewatkan ya!'},
        {'user_id': UID, 'keyword': 'stok', 'target_phone': 'all', 'created_at': _ts(timedelta(days=20)),
         'response': 'Stok semua produk masih tersedia ya kak! Untuk info stok terkini silakan DM langsung atau cek katalog di bio kami.'},
        {'user_id': UID, 'keyword': 'ongkir', 'target_phone': 'all', 'created_at': _ts(timedelta(days=18)),
         'response': 'Ongkos kirim bervariasi:\n- Jabodetabek: Rp 10.000\n- Pulau Jawa: Rp 15.000\n- Luar Jawa: Rp 25.000\n\nGratis ongkir untuk pembelian min. Rp 100.000!'},
        {'user_id': UID, 'keyword': 'garansi', 'target_phone': 'all', 'created_at': _ts(timedelta(days=15)),
         'response': 'Produk kami bergaransi resmi 1 tahun! Jika ada kendala dalam masa garansi, hubungi CS kami dan kami akan bantu proses klaimnya.'},
        {'user_id': UID, 'keyword': 'payment', 'target_phone': 'all', 'created_at': _ts(timedelta(days=12)),
         'response': 'Metode pembayaran yang kami terima:\n- Transfer Bank (BCA, Mandiri, BNI, BRI)\n- GoPay, OVO, DANA, ShopeePay\n- COD (area tertentu)\n\nSemua transaksi aman!'},
        {'user_id': UID, 'keyword': 'alamat', 'target_phone': 'all', 'created_at': _ts(timedelta(days=10)),
         'response': 'Alamat toko kami:\nJl. Sudirman No. 123, Jakarta Pusat\n\nJam operasional:\nSenin-Sabtu: 09.00-21.00 WIB\nMinggu: 10.00-18.00 WIB'},
        {'user_id': UID, 'keyword': 'retur', 'target_phone': 'all', 'created_at': _ts(timedelta(days=8)),
         'response': 'Kebijakan retur kami:\n- Retur dalam 7 hari sejak barang diterima\n- Barang harus dalam kondisi original\n- Sertakan foto bukti kerusakan\n\nHubungi CS kami untuk proses retur.'},
        {'user_id': UID, 'keyword': 'grosir', 'target_phone': 'all', 'created_at': _ts(timedelta(days=5)),
         'response': 'Program Grosir & Reseller:\n- Min. order 10 pcs: Diskon 15%\n- Min. order 25 pcs: Diskon 25%\n- Min. order 50 pcs: Diskon 35%\n\nDaftar sebagai reseller kami sekarang!'},
        {'user_id': UID, 'keyword': 'cs', 'target_phone': 'all', 'created_at': _ts(timedelta(days=3)),
         'response': 'Tim CS kami siap melayani 24 jam:\n- WhatsApp: +62812-3456-7890\n- Email: cs@tokokami.com\n- Telegram: @cstokokami\n\nRespon rata-rata kurang dari 5 menit!'},
        {'user_id': UID, 'keyword': 'katalog', 'target_phone': 'all', 'created_at': _ts(timedelta(days=1)),
         'response': 'Katalog produk lengkap kami:\n- Website: www.tokokami.com\n- Instagram: @tokokami_official\n\nFollow akun kami untuk update produk & promo terbaru!'},
    ]
    res = supabase.table('keyword_rules').insert(keywords).execute()
    print(f"   {len(res.data)} keyword rules berhasil")

def seed_auto_reply_settings():
    print("Seeding auto_reply_settings...")
    settings = [
        {
            'user_id': UID, 'target_phone': 'all', 'is_active': True, 'cooldown_minutes': 60,
            'welcome_message': 'Halo kak! Terima kasih sudah menghubungi kami.\n\nKetik keyword berikut:\n- harga - Info harga produk\n- order - Cara pemesanan\n- promo - Promo aktif\n- stok - Cek stok produk\n- ongkir - Info ongkos kirim\n- garansi - Info garansi\n- cs - Customer service'
        },
        {
            'user_id': UID, 'target_phone': '+6281234567890', 'is_active': True, 'cooldown_minutes': 30,
            'welcome_message': 'Halo! Ini akun utama kami. Ada yang bisa dibantu? Ketik harga, order, atau promo untuk info cepat!'
        },
    ]
    res = supabase.table('auto_reply_settings').insert(settings).execute()
    print(f"   {len(res.data)} auto reply settings berhasil")

def seed_notifications():
    print("Seeding notifications...")
    notifs = [
        {'user_id': UID, 'is_read': False, 'type': 'success',
         'title': 'Blast Berhasil!',
         'message': '50 pesan berhasil dikirim ke grup target Promo Harian. Success rate: 90%.',
         'created_at': _ts(timedelta(minutes=30))},
        {'user_id': UID, 'is_read': False, 'type': 'warning',
         'title': 'FloodWait Terdeteksi',
         'message': 'Akun +6281234567890 mengalami FloodWait 30 detik pada grup Komunitas UMKM Yogyakarta.',
         'created_at': _ts(timedelta(hours=1))},
        {'user_id': UID, 'is_read': True, 'type': 'success',
         'title': 'Jadwal Blast Aktif',
         'message': 'Jadwal pukul 09:30 berhasil dijalankan. Template: Promo Diskon 50%.',
         'created_at': _ts(timedelta(hours=3))},
        {'user_id': UID, 'is_read': True, 'type': 'info',
         'title': 'Kontak CRM Diperbarui',
         'message': '50 kontak baru berhasil ditambahkan ke database CRM Anda.',
         'created_at': _ts(timedelta(hours=5))},
        {'user_id': UID, 'is_read': True, 'type': 'success',
         'title': 'Auto-Reply Aktif',
         'message': 'Sistem auto-reply berhasil diaktifkan untuk semua akun Telegram Anda.',
         'created_at': _ts(timedelta(days=1))},
        {'user_id': UID, 'is_read': True, 'type': 'success',
         'title': 'Pembayaran Diterima!',
         'message': 'Paket UMKM Pro (90 Hari) kini aktif hingga 27 Juni 2026. Selamat menikmati!',
         'created_at': _ts(timedelta(days=3))},
    ]
    res = supabase.table('notifications').insert(notifs).execute()
    print(f"   {len(res.data)} notifications berhasil")

def main():
    print("=== SEEDING DATA DEMO KE SUPABASE ===")
    print(f"User ID: {UID}\n")

    clear_old_data()
    print()
    seed_telegram_accounts()
    templates = seed_message_templates()
    seed_blast_targets()
    seed_blast_schedules(templates)
    seed_blast_logs()
    seed_crm_users()
    seed_keyword_rules()
    seed_auto_reply_settings()
    try:
        seed_notifications()
    except Exception as e:
        print(f"   notifications skipped: {e}")

    print("\n=== SELESAI! Semua data demo berhasil dimasukkan. ===")

if __name__ == '__main__':
    main()

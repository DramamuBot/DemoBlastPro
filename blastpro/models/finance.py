import re
import logging
import os
import time
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from extensions import supabase

logger = logging.getLogger("BlastPro_Core")


def _get_duration_title(days):
    if days <= 3:
        return "Trial"
    if days <= 35:
        return "Bulanan"
    if days <= 100:
        return "Quarterly"
    return "Semester"


def log_bank_mutation(bank_id, m_type, amount, bal_before, bal_after, desc):
    try:
        supabase.table('bank_mutations').insert({
            'bank_id': bank_id,
            'mutation_type': m_type,
            'amount': amount,
            'balance_before': bal_before,
            'balance_after': bal_after,
            'description': desc,
            'created_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        }).execute()
    except Exception as e:
        logger.error(f"Gagal catat mutasi: {e}")


class FinanceManager:

    @staticmethod
    def get_plans_structure():
        if not supabase:
            from local_data import get_local_plans
            return get_local_plans()

        try:
            plans = supabase.table('pricing_plans').select("*").order('id').execute().data
        except Exception as e:
            logger.error(f"DB Error Pricing Plans: {e}")
            return {}

        if not plans:
            return {}

        structured_data = {}

        for p in plans:
            try:
                variants = supabase.table('pricing_variants').select("*").eq('plan_id', p['id']).order('duration_days').execute().data
            except Exception as e:
                logger.error(f"DB Error Pricing Variants: {e}")
                variants = []
            structured_data[p['code_name']] = []

            for v in variants:
                sell_price = int(v.get('price_raw') or 0)
                raw_strike = str(v.get('price_strike') or '0')
                normal_price = int(re.sub(r'[^\d]', '', raw_strike)) if raw_strike.strip() else 0

                coret_text = ""
                hemat_text = ""

                if normal_price > sell_price and sell_price > 0:
                    coret_text = f"Rp {normal_price:,.0f}".replace(',', '.')
                    persen = int(round(((normal_price - sell_price) / normal_price) * 100))
                    selisih = normal_price - sell_price
                    if selisih >= 1000000:
                        hemat_text = f"Hemat {selisih/1000000:g} Juta"
                    elif selisih >= 1000:
                        hemat_text = f"Hemat {int(selisih/1000)}Rb"
                    else:
                        hemat_text = f"Hemat {persen}%"

                structured_data[p['code_name']].append({
                    'id': v['id'],
                    'title': _get_duration_title(v['duration_days']),
                    'duration': f"{v['duration_days']} Hari",
                    'price': v['price_display'],
                    'rawPrice': sell_price,
                    'coret': coret_text,
                    'hemat': hemat_text,
                    'features': p['features'],
                    'btnText': "Pilih Paket",
                    'bestValue': v.get('is_best_value', False)
                })

        return structured_data

    @staticmethod
    def create_transaction(user_id, variant_id, method, proof_file=None):
        if not supabase:
            return False, "Database tidak terhubung."

        try:
            existing = supabase.table('transactions').select("id").eq('user_id', user_id).eq('status', 'pending').execute()
            if existing.data:
                return False, "Kamu masih memiliki pembayaran yang menunggu konfirmasi admin. Tunggu atau hubungi support."

            var_res = supabase.table('pricing_variants').select("price_raw").eq('id', variant_id).execute()
            if not var_res.data:
                return False, "Paket tidak valid"

            amount = var_res.data[0]['price_raw']
            if amount is None:
                return False, "Harga paket tidak valid, hubungi administrator."
            amount = int(amount)

            proof_path = None
            if proof_file:
                os.makedirs('static/uploads/proofs', exist_ok=True)
                filename = secure_filename(f"proof_{user_id}_{int(time.time())}_{proof_file.filename}")
                proof_path = f"/static/uploads/proofs/{filename}"
                proof_file.save(os.path.join('static/uploads/proofs', filename))

            data = {
                'user_id': user_id,
                'plan_variant_id': variant_id,
                'amount': amount,
                'payment_method': method,
                'proof_url': proof_path,
                'status': 'pending'
            }
            supabase.table('transactions').insert(data).execute()
            return True, "Invoice berhasil dibuat"
        except Exception as e:
            logger.error(f"Create Transaction Error: {e}")
            return False, f"Gagal membuat invoice: {str(e)}"

    @staticmethod
    def approve_transaction(trx_id, admin_id, admin_note=""):
        from services.helpers import send_telegram_alert, save_notification
        try:
            trx = supabase.table('transactions').select("*, pricing_variants(*, pricing_plans(display_name))")\
                .eq('id', trx_id).single().execute().data

            if not trx:
                return False, "Transaksi tidak ditemukan"
            if trx.get('status') == 'approved':
                return False, "Transaksi ini sudah pernah di-approve sebelumnya!"

            user_id = trx['user_id']
            duration = trx['pricing_variants']['duration_days']
            plan_name = trx['pricing_variants']['pricing_plans']['display_name']
            amount = float(trx['amount'])
            payment_method = trx.get('payment_method', '')

            u_res = supabase.table('users').select("subscription_end").eq('id', user_id).single().execute()
            current_end = u_res.data.get('subscription_end')

            now = datetime.utcnow()
            if current_end:
                parsed = datetime.fromisoformat(current_end.replace('Z', '+00:00'))
                if parsed.tzinfo is not None:
                    current_date = parsed - parsed.utcoffset()
                    current_date = current_date.replace(tzinfo=None)
                else:
                    current_date = parsed
                start_date = current_date if current_date > now else now
            else:
                start_date = now

            new_expiry = (start_date + timedelta(days=duration)).isoformat()

            supabase.table('users').update({
                'plan_tier': plan_name,
                'subscription_end': new_expiry
            }).eq('id', user_id).execute()

            note_text = admin_note if admin_note else f"Approved by Admin #{admin_id} at {now.strftime('%d/%m/%Y %H:%M')}"
            supabase.table('transactions').update({
                'status': 'approved',
                'admin_note': note_text
            }).eq('id', trx_id).execute()

            if payment_method:
                bank_res = supabase.table('admin_banks').select("id, balance").ilike('bank_name', f"%{payment_method}%").limit(1).execute()
                if bank_res.data:
                    bank_id = bank_res.data[0]['id']
                    current_balance = float(bank_res.data[0].get('balance') or 0)
                    new_balance = current_balance + amount
                    supabase.table('admin_banks').update({'balance': new_balance}).eq('id', bank_id).execute()
                    log_bank_mutation(bank_id, 'INCOME', amount, current_balance, new_balance, f"Auto: Pembayaran {plan_name} User #{user_id}")

            send_telegram_alert(user_id, f"✅ **Pembayaran Diterima!**\nPaket {plan_name} aktif sampai {new_expiry[:10]}.")
            save_notification(user_id, 'Pembayaran Disetujui!',
                              f'Paket {plan_name} kini aktif hingga {new_expiry[:10]}. Selamat menikmati fitur premium!',
                              'success')

            return True, "Sukses Approve & Saldo Bank Terupdate"
        except Exception as e:
            logger.error(f"Approval Error: {e}")
            return False, str(e)

    @staticmethod
    def reject_transaction(trx_id, admin_id, reason=""):
        from services.helpers import send_telegram_alert, save_notification
        try:
            trx = supabase.table('transactions').select(
                "*, pricing_variants(pricing_plans(display_name))"
            ).eq('id', trx_id).single().execute().data

            if not trx:
                return False, "Transaksi tidak ditemukan"
            if trx.get('status') != 'pending':
                return False, "Hanya transaksi berstatus pending yang bisa ditolak!"

            user_id = trx['user_id']
            plan_name = trx['pricing_variants']['pricing_plans']['display_name']
            now = datetime.utcnow()
            note_text = reason if reason else f"Ditolak oleh Admin #{admin_id} pada {now.strftime('%d/%m/%Y %H:%M')}"

            supabase.table('transactions').update({
                'status': 'rejected',
                'admin_note': note_text
            }).eq('id', trx_id).execute()

            send_telegram_alert(user_id,
                f"❌ **Pembayaran Ditolak**\n"
                f"Permintaan upgrade paket {plan_name} Anda ditolak.\n"
                f"Alasan: {reason or 'Tidak ada keterangan'}\n"
                f"Hubungi admin untuk informasi lebih lanjut."
            )
            save_notification(user_id, 'Pembayaran Ditolak',
                f'Permintaan {plan_name} ditolak. Alasan: {reason or "Hubungi admin"}',
                'error'
            )
            return True, "Transaksi berhasil ditolak dan notifikasi terkirim ke user."
        except Exception as e:
            logger.error(f"Reject Transaction Error: {e}")
            return False, str(e)

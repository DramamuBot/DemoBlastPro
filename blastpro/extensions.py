import logging
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, MASTER_KEY
from utils.security import CryptoEngine

logger = logging.getLogger("BlastPro_Core")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase API Connected Successfully.")
    except Exception as e:
        logger.error(f"❌ Supabase Connection Failed: {e}")
        supabase = None
else:
    logger.warning("⚠️ Supabase tidak dikonfigurasi (SUPABASE_URL/KEY kosong). Aplikasi berjalan dalam mode demo lokal.")

crypto_engine: CryptoEngine = None
if MASTER_KEY:
    try:
        crypto_engine = CryptoEngine(MASTER_KEY)
        logger.info("✅ CryptoEngine aktif. Session Telegram akan dienkripsi di DB.")
    except Exception as e:
        logger.warning(f"⚠️ CryptoEngine gagal inisialisasi ({e}). Session TIDAK terenkripsi.")
else:
    logger.warning("⚠️ MASTER_KEY belum diset. Session Telegram disimpan TANPA enkripsi.")


def encrypt_session(s: str) -> str:
    if crypto_engine and s:
        try:
            return crypto_engine.encrypt_data(s)
        except Exception as e:
            logger.error(f"[CRYPTO] Gagal enkripsi session: {e}")
    return s


def decrypt_session(s: str) -> str:
    if crypto_engine and s:
        try:
            return crypto_engine.decrypt_data(s)
        except Exception as e:
            logger.error(f"[CRYPTO] Gagal dekripsi session: {e}")
    return s


login_states = {}
failed_logins = {}
failed_resets = {}
qr_sessions = {}
qr_states = {}
broadcast_states = {}

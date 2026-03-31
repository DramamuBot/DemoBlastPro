from config import SECRET_KEY
from utils.security import TokenManager

token_manager = TokenManager(secret_key=SECRET_KEY)

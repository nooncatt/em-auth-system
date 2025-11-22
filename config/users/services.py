# bcrypt (хэширование паролей) & PyJWT (генерация токенов)
# проверка пароля
# декодирование токена
from hashlib import algorithms_available
import bcrypt
import jwt
from datetime import datetime, timedelta
from django.conf import settings


def hash_password(password: str):
    password_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_password.decode("utf-8")  # в БД — строка


def verify_password(password: str, password_hash: str):
    raw_bytes = password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")
    # compare
    return bcrypt.checkpw(raw_bytes, hash_bytes)


JWT_ALGORITHM = "HS256"
JWT_LIFETIME_MINUTES = 60  # token living time


def create_access_token(user_id: int):
    now = datetime.utcnow()
    payload = {
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_LIFETIME_MINUTES),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token  # str


def decode_access_token(token: str):
    """
    Пока просто декодер. Middleware/permissions будем писать позже
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return payload

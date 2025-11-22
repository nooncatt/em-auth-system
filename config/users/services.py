# bcrypt (хэширование паролей) & PyJWT (генерация токенов)
# проверка пароля
# декодирование токена

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


# h = hash_password("123456")
# print(h)
#
# print(check_password("123456", h))  # True
# print(check_password("wrong", h))  # False

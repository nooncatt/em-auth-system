# bcrypt (хэширование паролей) & PyJWT (генерация токенов)
# проверка пароля
# декодирование токена
import bcrypt
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from typing import Optional
from django.http import HttpRequest
from .models import User


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


def get_user_from_request(request: HttpRequest) -> Optional[User]:
    """
    Универсальный способ достать текущего пользователя:
    1) сначала смотрим на request.user / request.api_user (middleware)
    2) если там пусто – читаем Authorization и декодируем JWT.
    """
    django_request = getattr(request, "_request", request)

    # 1. Если middleware уже положила пользователя
    user = getattr(django_request, "user", None) or getattr(
        django_request, "api_user", None
    )
    if isinstance(user, User) and user.is_active:
        return user

    # 2. Пробуем прочитать заголовок Authorization
    auth_header = (
        django_request.META.get("HTTP_AUTHORIZATION")
        or django_request.headers.get("Authorization")
        or ""
    )
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1].strip().strip('"')

    try:
        payload = decode_access_token(token)
    except Exception as e:
        print("JWT ERROR get_user_from_request:", e)
        return None

    user_id = payload.get("user_id")
    if not user_id:
        return None

    return User.objects.filter(id=user_id, is_active=True).first()

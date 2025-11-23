from django.utils.deprecation import MiddlewareMixin
from users.models import User
from users.services import decode_access_token


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # read header
        auth_header = (
            request.META.get("HTTP_AUTHORIZATION")
            or request.headers.get("Authorization")
            or ""
        )

        # if no header – anonim
        if not auth_header:
            request.user = None
            return

        # "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            request.user = None
            return

        token = parts[1].strip().strip('"')

        # try to decode token and find user
        try:
            payload = decode_access_token(token)
            user_id = payload["user_id"]
            user = User.objects.filter(id=user_id, is_active=True).first()
            # наш пользователь кладётся в отдельное поле
            request.api_user = user
        except Exception as e:
            print("JWT ERROR:", e)
            request.api_user = None
        # try:
        #     payload = decode_access_token(token)
        #     user_id = payload["user_id"]
        #     user = User.objects.filter(id=user_id).first()
        #     request.user = user
        # except Exception:
        #     request.user = None

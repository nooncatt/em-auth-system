from django.utils.deprecation import MiddlewareMixin
from users.services import get_user_from_request


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # по умолчанию
        request.api_user = None

        user = get_user_from_request(request)
        if user is not None:
            request.user = user
            request.api_user = user

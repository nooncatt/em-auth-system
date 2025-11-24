from http import HTTPStatus

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User, AccessRule
from .permissions import IsAdminRole
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    LoginSerializer,
    MeUpdateSerializer,
    AccessRuleSerializer,
)
from .services import create_access_token, decode_access_token, get_user_from_request


# POST /api/auth/register
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            data = UserSerializer(user).data
            return Response(data, status=HTTPStatus.CREATED)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)


# POST /api/auth/login/
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, HTTPStatus.BAD_REQUEST)

        user = serializer.validated_data["user"]
        token = create_access_token(user.id)

        data = {
            "access_token": token,
            "token_type": "Bearer",
            "user": UserSerializer(user).data,
        }

        return Response(data, HTTPStatus.OK)


class MeView(APIView):
    def _get_current_user(self, request):
        user = get_user_from_request(request)
        print("VIEW USER:", user, type(user))
        return user

    # GET /api/me/
    def get(self, request):
        user = self._get_current_user(request)
        if user is None:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                HTTPStatus.UNAUTHORIZED,
            )
        return Response(UserSerializer(user).data, HTTPStatus.OK)

    # PATCH /api/me/
    def patch(self, request):
        user = self._get_current_user(request)
        if user is None:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                HTTPStatus.UNAUTHORIZED,
            )

        serializer = MeUpdateSerializer(
            data=request.data,
            context={"user": user},
            partial=True,
        )
        if not serializer.is_valid():
            return Response(serializer.errors, HTTPStatus.BAD_REQUEST)

        data = serializer.validated_data
        if "full_name" in data:
            user.full_name = data["full_name"]
        if "email" in data:
            user.email = data["email"]

        user.save()
        return Response(UserSerializer(user).data, HTTPStatus.OK)

    # DELETE /api/me/ — мягкое удаление
    def delete(self, request):
        user = self._get_current_user(request)
        if user is None:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                HTTPStatus.UNAUTHORIZED,
            )

        user.is_active = False
        user.save()
        return Response(status=HTTPStatus.NO_CONTENT)


class LogoutView(APIView):
    def post(self, request):
        # Для stateless JWT мы на сервере ничего не храним,
        # поэтому просто говорим клиенту "ок, считай себя разлогиненным".
        return Response({"detail": "Logged out"}, HTTPStatus.OK)


class AccessRuleListCreateView(ListCreateAPIView):
    queryset = AccessRule.objects.select_related("role", "element")
    serializer_class = AccessRuleSerializer
    permission_classes = [IsAdminRole]


class AccessRuleDetailView(RetrieveUpdateDestroyAPIView):
    queryset = AccessRule.objects.select_related("role", "element")
    serializer_class = AccessRuleSerializer
    permission_classes = [IsAdminRole]

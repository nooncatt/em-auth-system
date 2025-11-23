from http import HTTPStatus
from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    LoginSerializer,
    MeUpdateSerializer,
)
from .services import create_access_token, decode_access_token


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
        django_request = getattr(request, "_request", request)
        user = getattr(django_request, "api_user", None)

        print("VIEW USER:", user, type(user))

        # check it's users.User, notAnonymousUser
        if isinstance(user, User) and user.is_active:
            return user
        return None

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

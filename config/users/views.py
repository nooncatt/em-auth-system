from http import HTTPStatus
from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
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


# GET /api/me
# PATCH /api/me
class MeView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user = getattr(request, "user", None)

        # если middleware не подтянул юзера — вернём 401, а не 500
        if not isinstance(user, User):
            return Response(
                {"detail": "Authentication credentials were not provided."},
                HTTPStatus.UNAUTHORIZED,
            )
        data = UserSerializer(user).data
        return Response(data, HTTPStatus.OK)

    def patch(self, request):
        user = getattr(request, "user", None)
        if user is None:
            pass

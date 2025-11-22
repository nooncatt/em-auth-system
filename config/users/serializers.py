# RegisterSerializer
# LoginSerializer
# UserSerializer
from rest_framework import serializers
from .models import User


# регистрируем пользователя
# todo: check what we haven't user with the same email
# todo: password and next password compare
# todo: create user with this email and password and other data
# todo: if login() check password as: from .services import check_password


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "is_active",
            "created_at",
            "updated_at",
        ]


class UserSerializer(serializers.ModelSerializer):
    pass

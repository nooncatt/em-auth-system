# RegisterSerializer
# LoginSerializer
# UserSerializer
from rest_framework import serializers
from .models import User, Role
from .services import hash_password, verify_password


# class and funcs to register user
class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    password_repeat = serializers.CharField(min_length=6, write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_repeat"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def validate_email(self, email_str):
        if User.objects.filter(email=email_str.lower()).exists():
            raise serializers.ValidationError("User with this email already exists")
        return email_str.lower()

    def create(self, validated_data):
        full_name = validated_data["full_name"]
        email = validated_data["email"]
        password = validated_data["password"]

        # default role — user
        default_role, _ = Role.objects.get_or_create(name="user")

        user = User.objects.create(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role=default_role,
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        ]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].lower()
        password = attrs["password"]

        # try to find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        # check if user is_active
        if not user.is_active:
            raise serializers.ValidationError("User is inactive")

        # check password
        if not verify_password(password, user.password_hash):
            raise serializers.ValidationError("Invalid email or password")

        # put the found user inside validated_data to get it into the views.py
        attrs["user"] = user
        return attrs


class MeUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255, required=False)
    email = serializers.EmailField(required=False)

    def validate_email(self, email_str):
        email_str = email_str.lower()
        user = self.context["user"]
        # you can't use an email that another user already has
        if User.objects.filter(email=email_str).exclude(id=user.id).exists():
            raise serializers.ValidationError("User with this email already exists")
        return email_str

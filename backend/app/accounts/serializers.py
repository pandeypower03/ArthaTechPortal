from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, USERNAME_REGEX


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=254)   # email or username
    password = serializers.CharField(write_only=True, max_length=128)


class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.RegexField(USERNAME_REGEX)
    full_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, validators=[validate_password])


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "full_name", "is_active", "is_superuser"]
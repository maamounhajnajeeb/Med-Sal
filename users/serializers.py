from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from .models import Users
from service_providers.models import ServiceProvider


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()


class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = ("business_name", "contact_number")


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = Users
        fields = UserCreateSerializer.Meta.fields


"""
{
    "user_type": "SERVICE_PROVIDER",
    "email": "provider@example.com",
    "password": "your_password",
    "re_password": "your_password",
    "business_name": "Your Business Name",
    "contact_number": "123-456-7890",
    "bank_name": "Your Bank Name",
    "category": "DOCTOR",
    "iban": "Your IBAN",
    "swift_code": "Your Swift Code"
    "provider_file": "service provider documents"
}


"""


"""

{
    "user_type": "USER",
    "email": "user@example.com",
    "password": "your_password",
    "re_password": "your_password"
}


"""


"""
{"code": "344639"}
"""


"""

{"email": "admin@admin.com"}


"""

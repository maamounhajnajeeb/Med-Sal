from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from .models import Users
from service_providers.models import ServiceProvider

<<<<<<< HEAD
from django.contrib.auth.hashers import make_password

from . import models
from service_providers.models import ServiceProvider
from category.models import Category
=======
>>>>>>> 2fdb9f7c5f6430580c04aef87337da0a97069d11

class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()


class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
<<<<<<< HEAD
        fields = (
            "email", "password", "image", "user_type",
            )
    
    def validate(self, attrs):
        
        password = attrs.get("password")
        confirm_password = self.initial_data.get("confirm_password")
        if not (password or confirm_password):
            raise serializers.ValidationError(
                "password fields are required")
        
        if password != confirm_password:
            raise serializers.ValidationError(
                "passwords are not the same")
        
        attrs["password"] = self.encrypt_password(password)
        
        email = attrs.get("email")
        if not email:
            raise serializers.ValidationError(
                "email is field required")
        
        user_type = attrs.get("user_type")
        added_attrs = self.user_attrs_mapping(user_type)
        attrs = self.assign_attrs(attrs, added_attrs)
        
        return attrs
    
    def encrypt_password(self, password):
        return make_password(password=password)
    
    def user_attrs_mapping(self, user_type):
        hash_map = {
            "USER": [("is_active", False)]
            , "SERVICE_PROVIDER": [("is_active", False)]
            , "ADMIN": [("is_active", True), ("is_staff", True)]
            , "SUPER_ADMIN" : [("is_active", True), ("is_superuser", True), ("is_staff", True)]
        }
        return hash_map[user_type]
    
    def assign_attrs(self, original_attrs, added_attrs):
        if added_attrs:
            for attr in added_attrs:
                original_attrs[attr[0]] = attr[1]
        return original_attrs
    
    def save(self, **kwargs):
        user_instance = super().save(**kwargs)
        if self.initial_data.get("category"):
            self.create_service_provider(user_instance)
        return user_instance
    
    
    def create_service_provider(self, user_instance):
        data = self.initial_data
        category_instance = Category.objects.get(id=data["category"])
        
        ServiceProvider.objects.create(
            category=category_instance, business_name=data["bussiness_name"]
            , contact_number=data["contact_number"], bank_name=data["bank_name"]
            , iban=data["iban"], swift_code=data["swift_code"]
            , provider_file=data["provider_file"], user=user_instance
        )
=======
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
>>>>>>> 2fdb9f7c5f6430580c04aef87337da0a97069d11

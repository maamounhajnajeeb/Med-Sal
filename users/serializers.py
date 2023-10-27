from rest_framework import serializers

from django.contrib.auth.hashers import make_password

from . import models
from service_providers.models import ServiceProvider
from category.models import Category

class UsersSerializer(serializers.ModelSerializer):
    
    class Meta:
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
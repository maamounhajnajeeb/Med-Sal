from rest_framework import serializers

from django.contrib.auth.hashers import make_password

from . import models

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
        if user_type != "USER":
            attrs.setdefault("is_staff", True)
            attrs.setdefault("user_type", models.Users.Types.ADMIN)
            if user_type == "SUPER_ADMIN":
                attrs.setdefault("is_superuser", True)
                attrs.setdefault("user_type", models.Users.Types.SUPER_ADMIN)
        
        return attrs
    
    def encrypt_password(self, password):
        return make_password(password=password)
    
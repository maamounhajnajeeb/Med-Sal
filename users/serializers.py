from rest_framework import serializers

from . import models

class UsersSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = (
            "email", "password", "image", "user_type",
            )
    
    def validate(self, attrs):
        password = attrs.get("password")
        if not password:
            raise serializers.ValidationError(
                "password field is required")
        
        confirm_password = self.initial_data.get("confirm_password")
        if password != confirm_password:
            raise serializers.ValidationError(
                "passwords are not the same")
        
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
    
    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.set_password(instance.password)
        instance.save()
        
        return instance
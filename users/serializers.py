from rest_framework import serializers

from . import models


class UsersSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Users
        fields = (
            "email", "password", "image", "user_type",
            )
    
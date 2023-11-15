from rest_framework import serializers

from django.contrib.auth import models


class GroupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Group
        fields = "__all__"


class PermissionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Permission
        fields = "__all__"

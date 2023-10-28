from rest_framework import serializers
from category.models import *


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.StringRelatedField()
    
    class Meta:
        model = Category
        fields = ["id", "name", "parent"]
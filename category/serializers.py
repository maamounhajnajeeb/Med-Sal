from rest_framework import serializers

from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField

from .models import MyCategory


class CategorySerializer(serializers.ModelSerializer):
    
    parent = serializers.StringRelatedField()
    
    class Meta:
        model = MyCategory
        fields = "__all__"

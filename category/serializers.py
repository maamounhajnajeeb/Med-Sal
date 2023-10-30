from rest_framework import serializers

from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField

from .models import Category, MyCategory

class CategorySerializer(serializers.ModelSerializer):
    
    parent = serializers.StringRelatedField()
    
    class Meta:
        model = Category
        fields = "__all__"


class MyCategorySerializer(TranslatableModelSerializer):
    
    # parent = serializers.StringRelatedField()
    translations = TranslatedFieldsField(shared_model=MyCategory)
    
    class Meta:
        model = MyCategory
        fields = "__all__"

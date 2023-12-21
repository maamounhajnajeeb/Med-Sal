from rest_framework import serializers

from django.db import connection

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        language = kwargs.get('language')
        if language:
            self.language = kwargs.pop("language")
        else:
            self.language = None
    
    def create(self, validated_data):
        query = f"insert into category_category (en_name, ar_name) \
            values ('{validated_data['en_name']}', '{validated_data['ar_name']}')"
        
        if validated_data.get("parent"):
            query = f"insert into category_category (en_name, ar_name, parent_id) \
                values ('{validated_data['en_name']}', '{validated_data['ar_name']}' \
                , '{validated_data['parent'].id}')"
        
        with connection.cursor() as cursor:
            cursor.execute(query)
            
        return Category.objects.all().last()
    
    def to_representation(self, instance: Category):
        return {
            "id": instance.id
            , "name": instance.en_name if self.language == "en" else instance.ar_name
            , "parent": instance.parent
        }

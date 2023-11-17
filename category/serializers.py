from rest_framework import serializers

from django.db import connection
from rest_framework.fields import empty

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)
        
        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
    
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

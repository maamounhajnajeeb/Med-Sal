from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    
    name = serializers.SerializerMethodField()
    
    def __init__(self, instance=None, data=..., **kwargs):
        self.lang = kwargs.pop("lang", None)
        super().__init__(instance, data, **kwargs)
    
    def get_name(self, obj):
        return obj.name["langs"][self.lang]
    
    class Meta:
        model = Category
        fields = "__all__"
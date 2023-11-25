from rest_framework import serializers

from . import models

from category.serializers import CategorySerializer
from service_providers.models import ServiceProviderLocations



class StockSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.ProductStock
        fields = "__all__"


class ProudctSerializer(serializers.ModelSerializer):
    quantity = StockSerializer(many=False)
    service_provider_location = ServiceProviderLocations()
    
    class Meta:
        model = models.Product
        fields = "__all__"
        
    def validate(self, attrs):
        attrs = super().validate(attrs)
        quantity = attrs.get("quantity")
        if quantity:
            quantity_obj = models.ProductStock.objects.create(**quantity)
            attrs["quantity"] = quantity_obj
        
        return attrs
    
    def get_category(self, obj: models.Product):
        category = obj.service_provider_location.service_provider.category
        serializer = CategorySerializer(category, many=False)
        
        return serializer.data
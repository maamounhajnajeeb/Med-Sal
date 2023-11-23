from rest_framework import serializers

from typing import Any

from . import models

from category.serializers import CategorySerializer
from service_providers.models import ServiceProviderLocations


class StockSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.ProductStock
        fields = "__all__"


class ProudctSerializer(serializers.ModelSerializer):
    quantity = StockSerializer()
    service_provider_location = ServiceProviderLocations()
    
    class Meta:
        model = models.Product
        fields = "__all__"
        
    def validate(self, attrs):
        attr = super().validate(attrs)
        quantity = attr.get("quantity")
        quantity_obj = models.ProductStock.objects.create(**quantity)
        
        attr["quantity"] = quantity_obj
        return attr
    
    # def create(self, validated_data):
    #     return super().create(validated_data)
    # def create(self, validated_data: dict[str, Any]):
    #     product = models.Product.objects.create(**validated_data)
    #     return product
        
    def get_category(self, obj: models.Product):
        category = obj.service_provider_location.service_provider.category
        serializer = CategorySerializer(category, many=False)
        
        return serializer.data
from rest_framework import serializers

from . import models



class StockSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.ProductStock
        fields = "__all__"


class ProudctSerializer(serializers.ModelSerializer):
    quantity = StockSerializer()
    
    class Meta:
        model = models.Product
        fields = "__all__"

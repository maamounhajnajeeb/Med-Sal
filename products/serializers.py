from rest_framework import serializers

from django.db.models import Avg
from rest_framework.fields import empty

from . import models

from service_providers.models import ServiceProviderLocations



class RateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.ProductRates
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        fields = kwargs.get("fields")
        if not fields:
            self.language = None
        else:
            fields = kwargs.pop("fields")
            self.language = fields.get("language")
        
        super().__init__(instance, data, **kwargs)
        
    def validate(self, attrs):
        rate = attrs.get("rate")
        if int(rate) > 5 or int(rate) < 0:
            raise ValueError("Product Rate must be under 5 and more than or equal 0")
        
        return super().validate(attrs)
    
    def to_representation(self, instance: models.ProductRates):
        response = super().to_representation(instance)
        response["product_title"] = instance.product.ar_title if self.language == "ar" else instance.product.en_title
        response["user_email"] = instance.user.email
        
        return response


class ProudctSerializer(serializers.ModelSerializer):
    service_provider_location = ServiceProviderLocations()
    
    class Meta:
        model = models.Product
        fields = ("id", "service_provider_location", "quantity", "ar_title"
                , "en_title", "ar_description", "en_description", "images", "price", )
    
    def __init__(self, instance=None, data=..., **kwargs):
        fields = kwargs.get("fields")
        if not fields:
            self.language = None
        else:
            fields = kwargs.pop("fields")
            self.language = fields.get("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance: models.Product):
        return {
            "id": instance.id
            , "service_provider": instance.service_provider_location.service_provider.business_name
            , "service_provider_location": instance.service_provider_location.id
            , "quantity": instance.quantity
            , "title": instance.ar_title if self.language == "ar" else instance.en_title
            , "description": instance.ar_description if self.language == "ar" else instance.en_description
            , "images": instance.images.split(",")
            , "price": instance.price
            , "rates": {
                "avg_rate": instance.product_rates.aggregate(Avg("rate"))
                , "5": instance.product_rates.filter(rate=5).count()
                , "4": instance.product_rates.filter(rate=4).count()
                , "3": instance.product_rates.filter(rate=3).count()
                , "2": instance.product_rates.filter(rate=2).count()
                , "1": instance.product_rates.filter(rate=1).count()
                , "0": instance.product_rates.filter(rate=0).count()
            }
        }

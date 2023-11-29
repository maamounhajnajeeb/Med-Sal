from rest_framework import serializers

from . import models

from service_providers.models import ServiceProviderLocations



class ProudctSerializer(serializers.ModelSerializer):
    service_provider_location = ServiceProviderLocations()
    
    class Meta:
        model = models.Product
        fields = ("id", "service_provider_location", "quantity", "ar_title"
                , "en_title", "ar_description", "en_description", "images", "price", )

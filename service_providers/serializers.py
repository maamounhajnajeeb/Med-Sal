from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import ServiceProvider, ServiceProviderLocations

class ServiceProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceProvider
        fields = '__all__'


# class ServiceProviderLocationSerializer(GeoFeatureModelSerializer):

#     class Meta:
#         model = ServiceProviderLocations
#         geo_field = 'location'
#         fields = ('service_provider_id',
#                   'opening',
#                   'closing',
#                   'crew',
#                   'created_at',
#                   )

class ServiceProviderLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderLocations
        fields = '__all__'
        read_only_fields = ('location', )
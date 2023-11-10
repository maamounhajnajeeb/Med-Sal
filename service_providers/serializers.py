from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import ServiceProvider, ServiceProviderLocations, UpdateRequest

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
        # read_only_fields = ('location', )


class CalculateDistanceSerializer(serializers.ModelSerializer):
    origin_lat = serializers.FloatField()
    origin_lng = serializers.FloatField()
    domain = serializers.FloatField(required=False)

    class Meta:
        model = ServiceProviderLocations
        fields = ('location', 'origin_lat', 'origin_lng', 'domain')


class UpdatRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpdateRequest
        fields = '__all__'
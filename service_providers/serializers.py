from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from django.contrib.auth import get_user_model

from .models import ServiceProvider, ServiceProviderLocations, UpdateProfileRequests

Users = get_user_model()



class ServiceProviderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ServiceProvider
        fields = (
            'id', 'user', "category", "bank_name", "business_name"
            , "iban", "swift_code", "provider_file", "account_status"
            , )
        
    def validate(self, attrs):
        return super().validate(attrs)


class ServiceProviderUpdateRequestSerializer(serializers.ModelSerializer):
    sent_data = serializers.JSONField(required=True)
    
    class Meta:
        model = UpdateProfileRequests
        fields = '__all__'
    
    
class ServiceProviderApproveRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = UpdateProfileRequests
        fields = ['request_status', 'approved_by']


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

class LocationSerializerSafe(serializers.ModelSerializer):
    service_provider = serializers.StringRelatedField()
    
    class Meta:
        model = ServiceProviderLocations
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ServiceProviderLocations
        fields = '__all__'


class ServiceProviderLocationSerializer(serializers.ModelSerializer):
    service_provider = serializers.StringRelatedField()
    
    class Meta:
        model = ServiceProviderLocations
        fields = '__all__'


class CalculateDistanceSerializer(serializers.ModelSerializer):
    origin_lat = serializers.FloatField()
    origin_lng = serializers.FloatField()
    domain = serializers.FloatField(required=False)

    class Meta:
        model = ServiceProviderLocations
        fields = ('location', 'origin_lat', 'origin_lng', 'domain')

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
   
    def validate(self, data):
        sent_data = data['sent_data']

        for field_name, field_value in sent_data.items():
            # Check if the field name exists in the ServiceProvider model
            if not hasattr(ServiceProvider, field_name):
                raise serializers.ValidationError(f'Invalid field name: {field_name}')
            
        # Check if the 'account_status' field is present in the sent_data
        if 'account_status'in data['sent_data']:
            # Raise an error if the 'account_status' field is present
            raise serializers.ValidationError('Service providers cannot update the account_status ')

        if 'approved_by' in data['sent_data']:
        # Remove the 'approved_by' field from the sent_data
            raise serializers.ValidationError('Service providers cannot update the approved_by field ')
        
        if 'user_requested' not in data:
                data['user_requested'] = self.context['request'].user.id

        return super().validate(data)
    
    class Meta:
        model = UpdateProfileRequests
        fields = '__all__'
        read_only_fields = ['user_requested']
    
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

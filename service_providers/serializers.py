from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import ServiceProvider, ServiceProviderLocations

class ServiceProviderSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(max_length=64, required=True)
    # password = serializers.CharField(
    #     max_length=64
    #     , write_only=True
    #     , required=True
    #     , validators=[validate_password])
    # passowrd2 = serializers.CharField(max_length=64, validators=[validate_password], required=True)
    # user_type = serializers.CharField(max_length=16, required=True)
    # image = serializers.ImageField()
    
    class Meta:
        model = ServiceProvider
        fields = (
            'user', "category", "bank_name", "business_name"
            , "iban", "swift_code", "provider_file", "account_status"
            , )

    def validate(self, attrs):
        return super().validate(attrs)

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


# class UpdatRequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UpdateRequest
#         fields = '__all__'
from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password

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

class ServiceProviderLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceProviderLocations
        fields = '__all__'


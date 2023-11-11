from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password

from .models import ServiceProvider, ServiceProviderLocations

class ServiceProviderSerializer(serializers.ModelSerializer):
    
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

from rest_framework import serializers

from .models import ServiceProvider, ServiceProviderLocations

class ServiceProviderRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceProvider
        fields = '__all__'


class ServiceProviderLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceProviderLocations
        fields = '__all__'
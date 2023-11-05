from rest_framework import serializers, exceptions

from .models import ServiceProvider, ServiceProviderLocations

class ServiceProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceProvider
        fields = '__all__'


class ServiceProviderLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceProviderLocations
        fields = '__all__'


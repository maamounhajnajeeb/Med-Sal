from rest_framework import serializers

from .models import ServiceProviderRegistration

class ServiceProviderRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceProviderRegistration
        fields = '__all__'
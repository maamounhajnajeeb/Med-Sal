from rest_framework import generics, decorators
from rest_framework import permissions, status
from rest_framework.response import Response

from django.http import HttpRequest

from . import permissions as local_permissions
from . import models, serializers

from users.serializers import ServiceProviderSerializer


class LocationRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ServiceProviderLocations.objects
    serializer_class = serializers.LocationSerializerSafe
    permission_classes = (local_permissions.LocationsPermissions, )


class CreateLocation(generics.CreateAPIView):
    queryset = models.ServiceProviderLocations.objects
    serializer_class = serializers.LocationSerializer
    permission_classes = (local_permissions.LocationsPermissions, )


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def show_providers_locations(request: HttpRequest):
    """
    get all service providers locations in the Database
    for everybody
    """
    queryset = models.ServiceProviderLocations.objects.all()
    serializer = serializers.LocationSerializerSafe(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def show_provider_locations(request: HttpRequest, pk):
    """
    get specific service provider locations
    pk here is service_provider id
    for everybody
    """
    queryset = models.ServiceProviderLocations.objects.filter(service_provider=pk)
    serializer = serializers.LocationSerializerSafe(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def show_category_locations(request: HttpRequest, pk):
    """
    get all category service providers locations
    pk here is: category id
    for everybody
    """
    queryset = models.ServiceProviderLocations.objects.filter(service_provider__category=pk)
    serializer = serializers.LocationSerializerSafe(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def show_category_providers(request, pk):
    """
    get all category providers
    pk here is: category id
    for everybody
    """
    queryset = models.ServiceProvider.objects.filter(category=pk)
    serializer = ServiceProviderSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

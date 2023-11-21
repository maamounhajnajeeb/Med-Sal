from rest_framework import generics, decorators
from rest_framework import permissions, status
from rest_framework.response import Response

from . import permissions as local_permissions
from . import models, serializers



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
def show_provider_locations(request, pk):
    queryset = models.ServiceProviderLocations.objects.filter(service_provider=pk)
    serializer = serializers.LocationSerializerSafe(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def show_providers_locations(request):
    queryset = models.ServiceProviderLocations.objects.all()
    serializer = serializers.LocationSerializerSafe(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

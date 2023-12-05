from rest_framework import generics, decorators
from rest_framework import permissions, status
from rest_framework.response import Response

from django.http import HttpRequest

from . import permissions as local_permissions
from . import models, serializers

from users.serializers import ServiceProviderSerializer
from notification.models import Notification



class LocationRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ServiceProviderLocations.objects
    serializer_class = serializers.LocationSerializerSafe
    permission_classes = (local_permissions.LocationsPermissions, )


class CreateLocation(generics.CreateAPIView):
    queryset = models.ServiceProviderLocations.objects
    serializer_class = serializers.LocationSerializer
    permission_classes = (local_permissions.LocationsPermissions, )
    
    def create(self, request: HttpRequest, *args, **kwargs):
        data = request.data.copy()
        data["service_provider"] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email
            , receiver_type="Service_Provider"
            , ar_content="تم إضافة فرع جديد لمزود الخدمة"
            , en_content="a new branch added to your service provider")
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
def show_provider_locations(request: HttpRequest, pk: int):
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

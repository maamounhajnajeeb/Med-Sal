from rest_framework import viewsets
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import ServiceProvider, ServiceProviderLocations
from .serializers import ServiceProviderRegistrationSerializer, ServiceProviderLocationSerializer
from rest_framework.permissions import BasePermission


# class AdminPermission(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_superuser


class CRUDServiceProviders(viewsets.ModelViewSet):

    queryset = ServiceProvider.objects
    serializer_class = ServiceProviderRegistrationSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["first_name", ]
    
    def creat(self, request):
        serializer = ServiceProviderRegistrationSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data)
    
    
    def retrieve(self, request, pk = None):
        service_provider = ServiceProvider.objects.get(pk = pk)
        serializer = ServiceProviderRegistrationSerializer(service_provider)
        return Response(serializer.data)
    
    
    def get_service_providers(self, request):
        json_data = ServiceProvider.objects.all()
        serializer = ServiceProviderRegistrationSerializer(json_data, many = True)
        return Response(serializer.data)
    
    
    def destroy(self, request, pk=None):
        service_provider = ServiceProvider.objects.get(pk = pk)
        service_provider.delete()
        return Response({"message": "Service provider deleted successfully."})
    
    
    @action(methods=['POST'], detail=True, )#permission_classes=[AdminPermission])
    def approve(self, request, pk=None):
        service_provider = ServiceProvider.objects.get(pk = pk)
        
        new_status = request.data.get('account_status').upper()
        availabe_status = ['ACCEPTED', 'REJECTED', 'PENDING']

        if new_status in availabe_status:
            service_provider.account_status = service_provider.AccountStatus[new_status]
        else:
            return Response({f"You provided a nonable value, please provide a value from {availabe_status}"},status = status.HTTP_400_BAD_REQUEST)
        service_provider.save()
        return Response({"message": f"Service provider status have been changed to {new_status.lower().capitalize()} successfully. "}, status = status.HTTP_200_OK)  
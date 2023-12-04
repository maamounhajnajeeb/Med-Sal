from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpRequest

import geopy.distance

from .models import ServiceProvider, ServiceProviderLocations, UpdateProfileRequests
from . import permissions, serializers


class CRUDServiceProviders(viewsets.ModelViewSet):
    """
    return all service providers
    """
    queryset = ServiceProvider.objects
    serializer_class = serializers.ServiceProviderSerializer
    permission_classes = (IsAdminUser, )
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["first_name", ]
    http_method_names = ['get', 'retrieve', 'head']
    
    @action(['GET'], detail = True, permission_classes = (IsAuthenticated,) ) #, 
    def retrieve_profile(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ServiceProviderUpdateRequestViewSet(viewsets.ModelViewSet):
    """
    Path => http://127.0.0.1:8000/api/v1/service_providers/profile/update_requests
    
    GET Methods (Only Admins):
        -List update requests via url => http://127.0.0.1:8000/api/v1/service_providers/profile/update_requests
        -List a specific update request using request id via url => http://127.0.0.1:8000/api/v1/service_providers/profile/update_requests/<int:pk> 
    
    POST Method (Only Service Providers):
        -Create a new update request via url => http://127.0.0.1:8000/api/v1/service_providers/profile/update_requests/    
            -sent_data field is required (JSON field)
            
    PATCH Method (Only Admins):
        -Approve or decline an update request via url => http://127.0.0.1:8000/api/v1/service_providers/profile/update_requests/<int:pk>/approve_or_decline
            - request_status field is required (Approved or Declined)
    """
    
    queryset = UpdateProfileRequests.objects
    serializer_class = serializers.ServiceProviderUpdateRequestSerializer
    permission_classes = (permissions.UpdateRequestsPermission,)
    
    # Service_provider can send an update request
    def create(self, request: HttpRequest, *args, **kwargs):
        service_provider = request.user.service_provider
        request_data = request.data.copy()
        request_data["provider_requested"] = service_provider
        
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        serializer.save(checked_by=self.request.user)


class Location(APIView):
    serializer_class = serializers.ServiceProviderLocationSerializer
    
    def get(self,request):
        queryset = ServiceProviderLocations.objects.all()
        serializer = serializers.ServiceProviderLocationSerializer(queryset, many = True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = serializers.ServiceProviderLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class ServiceProviderDistanceListView(APIView):
    def post(self, request):
        serializer = serializers.CalculateDistanceSerializer(data=request.data)
        if serializer.is_valid():
            origin = geopy.Point(serializer.validated_data['origin_lat'], serializer.validated_data['origin_lng'])
            domain = serializer.validated_data.get('domain', 100)  # Default domain of 100 km
            
            service_provider_locations = ServiceProviderLocations.objects.all()
            results = []
            
            for location in service_provider_locations:
                destination = geopy.Point(location.location.y, location.location.x)
                distance = geopy.distance.distance(origin, destination).km
                
                if distance <= domain:
                    result = {
                        'service_provider':location.service_provider_id.business_name,
                        'distance':distance
                    }   
                    results.append(result) 
                    return Response(results, status=status.HTTP_200_OK)
                else:
                    return Response({'There is no service provider in the area you are searching in'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

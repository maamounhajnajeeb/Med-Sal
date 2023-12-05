from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework import decorators

from django.http import HttpRequest

import geopy.distance

from .models import ServiceProviderLocations, UpdateProfileRequests
from . import permissions, serializers

from notification.models import Notification



@decorators.api_view(["GET", ])
def check_provider_update_status(request: HttpRequest):
    print("ih")
    provider_id: int = request.user.id
    queryset = UpdateProfileRequests.objects.filter(provider_requested=provider_id)
    if not queryset.exists():
        return Response({
            "message": "there is no such record for this provider"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.ServiceProviderUpdateRequestSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceProviderUpdateRequestViewSet(viewsets.ModelViewSet):
    queryset = UpdateProfileRequests.objects
    serializer_class = serializers.ServiceProviderUpdateRequestSerializer
    permission_classes = (permissions.UpdateRequestsPermission, )
    
    # Service_provider can send an update request
    def create(self, request: HttpRequest, *args, **kwargs):
        service_provider, data = request.user.service_provider.id, request.data.copy()
        data["provider_requested"] = service_provider
        
        Notification.objects.create(
            sender="System", sender_type="System",
            receiver=request.user.email, receiver_type="Service_Provider",
            ar_content="تعديل الملف الشخصي بانتظار المراجعة",
            en_content="Profile information editing is under revision")
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request: HttpRequest, *args, **kwargs):
        data = request.data.copy()
        data["checked_by"] = request.user.id
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)


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

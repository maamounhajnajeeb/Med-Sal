from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpRequest

import geopy.distance

from .models import ServiceProvider, ServiceProviderLocations, UpdateProfileRequests
from . import permissions, serializers

from users.serializers import ServiceProviderSerializer


class CRUDServiceProviders(viewsets.ModelViewSet):
    
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
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_requested=service_provider)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        if resp.data.get("request_status") == "Accepted":
            updated_data = resp.data.get("sent_data")
            provider_id = resp.data.get("user_requested")
            provider_instance = ServiceProvider.objects.filter(id=provider_id)
            provider_instance.update(**updated_data)
            serializer = ServiceProviderSerializer(instance=provider_instance.first())
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        
        return Response(resp.data, status=resp.status_code)
    
    def perform_update(self, serializer):
        serializer.save(checked_by=self.request.user)
    
    # def approve_or_decline(self, request, pk):
    #     serializer = serializers.ServiceProviderApproveRequestSerializer(data = request.data)
        
    #     try:
    #         update_request = UpdateProfileRequests.objects.get(pk=pk)
    #         service_provider = ServiceProvider.objects.get(pk=update_request.user_requested.id)
    #     except (UpdateProfileRequests.DoesNotExist, ServiceProvider.DoesNotExist):
    #         return Response({"Error": f"Invalid update request or service provider id = {pk}"}, status=status.HTTP_404_NOT_FOUND)
        
    #     serializer = serializers.ServiceProviderApproveRequestSerializer(update_request, data=request.data)
        
    #     if serializer.is_valid():
    #         if request.data['request_status'].lower() == 'approved':
    #             service_provider.approved_by = self.request.user
    #             service_provider.account_status = ServiceProvider.AccountStatus.ACCEPTED
    #             sent_data = update_request.sent_data

    #             for key, value in sent_data.items():
    #                 setattr(service_provider, key, value)
    #             service_provider.save()

    #             update_request.approved_by = self.request.user
    #             update_request.request_status = 'approved'
    #             update_request.save()
    #             return Response({f"Profile data for user with id = {pk} updated successfully "}, status=status.HTTP_200_OK)

    #         elif request.data['request_status'].lower() == 'declined':
    #             update_request.request_status = 'declined'
    #             update_request.save()
    #             return Response({f"Update Profile data requets for user with id = {pk} has been declined "}, status=status.HTTP_200_OK)

    #         else:
    #             return Response({"Error":"request_status must be either approved or declined"},status=status.HTTP_400_BAD_REQUEST)
        
    #     serializer.save()
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

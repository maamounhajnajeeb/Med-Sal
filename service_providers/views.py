from rest_framework import viewsets, generics
from rest_framework import filters, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ServiceProvider, ServiceProviderLocations, UpdateProfileRequests
import geopy.distance
from service_providers import permissions, serializers
from users.models import Admins
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

class CRUDServiceProviders(viewsets.ModelViewSet):
    
    """
    List path => "api/v1/service_provider/"
    
    To retrieve a specific service_provider: path => "api/v1/service_providers/<id>/retrieve_profile"

    Permissions on methods:
        - Only admins can List all service providers data
        - Both authenticated users and admins can retrieve a specific service provider profile         
        
    Filtering:
        - You can order by any field you choose either in asc or desc order => api/v1/service_providers/?ordering=-password
        - You can search by name = > api/v1/service_providers/?search=<service_provider_name>
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
    
    queryset = UpdateProfileRequests.objects.all()
    serializer_class = serializers.ServiceProviderUpdateRequestSerializer
    permission_classes = (permissions.UpdateRequestsPermission,)

    # Service_provider can send an update request
    def create(self, request, *args, **kwargs):
        service_provider_id = request.user.id
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            service_provider = ServiceProvider.objects.get(pk=service_provider_id)
            serializer.save(user_requested = service_provider)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # Retrieve a specific update request using id
    def retrieve(self, request, pk=None):
        try:
            update_request = UpdateProfileRequests.objects.get(pk=pk)
        except UpdateProfileRequests.DoesNotExist:
            return Response({"Error": f"No update request found with id = {pk}"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(update_request)
        return Response(serializer.data)

    
    # Admin can approve or decline the request
    @action(['PATCH'],detail=True)
    def approve_or_decline(self, request, pk):
        serializer = serializers.ServiceProviderApproveRequestSerializer(data = request.data)
        
        try:
            update_request = UpdateProfileRequests.objects.get(pk=pk)
            service_provider = ServiceProvider.objects.get(pk=update_request.user_requested.id)
        except (UpdateProfileRequests.DoesNotExist, ServiceProvider.DoesNotExist):
            return Response({"Error": f"Invalid update request or service provider id = {pk}"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializers.ServiceProviderApproveRequestSerializer(update_request, data=request.data)
       
        if serializer.is_valid():
            if request.data['request_status'].lower() == 'approved':
                service_provider.approved_by = self.request.user
                service_provider.account_status = ServiceProvider.AccountStatus.ACCEPTED
                sent_data = update_request.sent_data

                for key, value in sent_data.items():
                    setattr(service_provider, key, value)
                service_provider.save()

                update_request.approved_by = self.request.user
                update_request.request_status = 'approved'
                update_request.save()
                return Response({f"Profile data for user with id = {pk} updated successfully "}, status=status.HTTP_200_OK)

            elif request.data['request_status'].lower() == 'declined':
                update_request.request_status = 'declined'
                update_request.save()
                return Response({f"Update Profile data requets for user with id = {pk} has been declined "}, status=status.HTTP_200_OK)

            else:
                return Response({"Error":"request_status must be either approved or declined"},status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # Admin can list all requests
    def list_requests(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
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

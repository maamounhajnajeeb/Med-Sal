from rest_framework import viewsets, permissions, generics
from rest_framework import filters, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ServiceProvider, ServiceProviderLocations
from service_providers import serializers 
import geopy.distance
from service_providers import permissions
from users.models import Admins
from rest_framework.permissions import IsAdminUser

class CRUDServiceProviders(viewsets.ModelViewSet):
    
    """
    List and Create: path => "api/v1/service_provider/"
    
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
    # permission_classes = (permissions.OnlyAdminsCanListPermissions, )
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["first_name", ]
    http_method_names = ['get', 'retrieve', 'head']


    @action(['GET'], detail = True) #, permission_classes = [UpdateAndRetrievePermissions, ] 
    def retrieve_profile(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    

class ServiceProviderUpdateRequestCreateAPI(APIView):
    """
        A service_provider can request an update for his profile by this API
        he should provide :
            -user_requested (his id) Note: this will be removed when we solve the password hashing problem so it can be done automatically and get the id from the user who requests
            -request_type (either update or create)
            -the data he want to update as a JSONfield data => sent_data:{data}
    """
    def post(self, request):
        serializer = serializers.ServiceProviderUpdateRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListUpdateRequests(generics.ListAPIView):
    """
        To list all update requests 
        Only Admins can access this API
    """
    # permission_classes = (IsAdminUser,)
    serializer_class = serializers.ServiceProviderUpdateRequestSerializer
    queryset = serializers.UpdateProfileRequests.objects.all()


class ServiceProviderApproveAPI(APIView):
    """
        Admins can approve or decline requests for service_providers by this API
        the admin should provide:
            - approved_or_declined ({approved} If he approve the request, {declined} If he decline the request)
            - approved_by (his id) Note: this will be removed when we solve the password hashing problem so it can be done automatically and get the id from the admin who requests
    """
    def post(self, request, pk):
        
        try:
            service_provider = ServiceProvider.objects.get(pk=pk)
            update_request = serializers.UpdateProfileRequests.objects.filter(user_requested=service_provider, request_type='update').first()

        except ServiceProvider.DoesNotExist:
            return Response({"Error":f"No service provider with id = {pk}"},status=status.HTTP_404_NOT_FOUND)
        
        if not update_request:
            return Response({"Error":f"service provider with id = {pk} did not requeted an update"},status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.ServiceProviderApproveRequestSerializer(update_request, data=request.data)

        if serializer.is_valid():
            serializer.save()

            if request.data['request_status'] == 'approved':
                admin_id = request.data['approved_by']
                
                # Updates in the ServiceProvider model
                service_provider.approved_by = Admins.objects.get(pk=admin_id)
                service_provider.account_status = ServiceProvider.AccountStatus.ACCEPTED
                sent_data = update_request.sent_data 
                
                # Update the service provider data with the updated values from the sent data
                for key, value in sent_data.items():
                    setattr(service_provider, key, value)
                service_provider.save()

                # Updates in the UpdateProfileRequests model
                update_request.approved_by = Admins.objects.get(pk=admin_id)
                update_request.request_status = 'approved'
                update_request.save()

            else:
                update_request.request_status = 'declined'
                update_request.save()

            return Response({f"Profile data for user with id = {pk} updated successfully "}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Location(APIView):
     serializer_class = serializers.ServiceProviderLocationSerializer

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

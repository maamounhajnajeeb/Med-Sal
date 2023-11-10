from rest_framework import viewsets
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ServiceProvider, ServiceProviderLocations
from .serializers import ServiceProviderSerializer, ServiceProviderLocationSerializer, CalculateDistanceSerializer
import geopy.distance
from .permissions import UpdateAndRetrievePermissions, ListAndCreatePermissions


class CRUDServiceProviders(viewsets.ModelViewSet):
    
    """
    List and Create: path => "api/v1/service_provider/"
    
    To retrieve a specific service_provider: path => "api/v1/service_providers/<id>/retrieve_profile"

    To update a specific service_provider: path => "api/v1/service_providers/<id>/update_profile"

    Permissions on methods:
        - Only admins can List all service providers data
        - Only NOT authenticated users can create a new service provider profile
        - Only admins can change account_status field for a specific service provider
        - Both authenticated users and admins can retrieve a specific service provider profile 
        - Either admins can edit a service provider profile or a service provider can edit his own profile
        
    Filtering:
        - You can order by any field you choose either in asc or desc order => api/v1/service_providers/?ordering=-password
        - You can search by name = > api/v1/service_providers/?search=<service_provider_name>
    """
    
    queryset = ServiceProvider.objects
    serializer_class = ServiceProviderSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["first_name", ]
    permission_classes = [ListAndCreatePermissions, ]

    # A function for updating a service_provider data (Admins only can update account_status field)
    @action(['PATCH'], detail=True, permission_classes = [UpdateAndRetrievePermissions,])
    def update_profile(self, request, *args, **kwargs):
        # Check if the user is trying to update the account_status field
        if request.data.get('account_status'):
            # Check If the user is a service provider, he can't update the account_status field
            if not request.user.is_staff:
                # Send an error response
                return Response({'Error': 'Service providers cannot update the account_status field'},status=status.HTTP_400_BAD_REQUEST)
            else:
                available_account_status = ['accepted','pending','rejected']
                new_account_status = request.data.get('account_status')
                # Check if the new account status is either accepted or pending or rejected
                if new_account_status in available_account_status:
                    # Update the account status
                    obj = ServiceProvider.objects.get(pk=kwargs['pk'])
                    obj.account_status = new_account_status
                    obj.save()
                    # Send a success response
                    return Response({'Message': f'Account status changed to {new_account_status}'})
                else:
                    # Send an error response
                    return Response({'Error': f'Account status should be in {available_account_status}'})
        return super().partial_update(request, *args, **kwargs)    
    
    
    # A function for retrieving a specific service_provider data 
    @action(['GET'], detail=True, permission_classes = [UpdateAndRetrievePermissions,])
    def retrieve_profile(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

        
class Location(APIView):
     serializer_class = ServiceProviderLocationSerializer

     def get(self,request):
          queryset = ServiceProviderLocations.objects.all()
          serializer = ServiceProviderLocationSerializer(queryset, many = True)
          return Response(serializer.data)
     
     def post(self,request):
        serializer = ServiceProviderLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class ServiceProviderDistanceListView(APIView):
    def post(self, request):
        serializer = CalculateDistanceSerializer(data=request.data)
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
        

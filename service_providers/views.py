from rest_framework import viewsets
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import ServiceProvider, ServiceProviderLocations
from .serializers import ServiceProviderSerializer, ServiceProviderLocationSerializer

from .permissions import UpdateAndDeletePermissions, ListAndCreatePermissions


    
class CRUDServiceProviders(viewsets.ModelViewSet):
    
    """
    List and Create: path => "api/v1/service_provider/"
    
    To retrieve a specific service_provider: path => "api/v1/service_providers/<id>/retrieve_profile"

    To update a specific service_provider: path => "api/v1/service_providers/<id>/update_profile"

    Permissions on methods:
        - Only admins can List all service providers data
        - Only NOT authenticated users can create a new service provider profile
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

    @action(['PATCH'], detail=True, permission_classes = [UpdateAndDeletePermissions,])
    def update_profile(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)    
    
    @action(['GET'], detail=True, permission_classes = [UpdateAndDeletePermissions,])
    def retrieve_profile(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@api_view(['GET', 'POST'])
def locationss(request):
        if request.method == 'GET':
            try:
                location = ServiceProviderLocations.objects.all()
                serializer = ServiceProviderLocationSerializer(location, many = True).data
                return Response(serializer, status=status.HTTP_200_OK)
            except:
                return Response({'Error':'Nothin found'})      
        elif request.method == 'POST':
            serializer = ServiceProviderLocationSerializer(data = request.data)
            serializer.is_valid(raise_exception = True)
            serializer.save()
            return Response({"done"})
        
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
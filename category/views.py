from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework import viewsets, decorators

from django.http import HttpRequest
from django.db.models import Q

from .models import Category
from .permissions import IsAdmin
from .helpers import choose_lang, searching_func
from .serializers import CategorySerializer

from service_providers.models import ServiceProvider, ServiceProviderLocations
from service_providers.serializers import LocationSerializerSafe

from functools import reduce



@decorators.api_view(["GET", ])
def parent_sub_category(request, pk):
    third_field = choose_lang(request)
    
    queryset = Category.objects.filter(parent=pk)
    serializer = CategorySerializer(queryset, fields={"id", "parent", third_field}, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def prime_categories(request):
    third_field = choose_lang(request)
    
    queryset = Category.objects.filter(parent=None)
    serializer = CategorySerializer(queryset, fields={"id", "parent", third_field}, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def search_category(request: HttpRequest):
    third_field = choose_lang(request)
    queryset = searching_func(request, third_field)
    
    if not queryset.exists():
        return Response({
            "message": "There is not result with this search key"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CategorySerializer(queryset, fields={"id", "parent", third_field}, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    path : "api/v1/category/"
    
    this view offers four api methods
    
    everybody method: get method (including: searching, listing and get specific record)
    admins methods: post, update[patch, put] and delete methods
    
    you can call specific category by its id
    also you can search for specific category by its name (via api/v1/category?serach=<category_name>)
    
    you can assign parent category for each sub category by using the parent id with the form data
    """
    
    serializer_class = CategorySerializer
    queryset = Category.objects
    permission_classes = (IsAdmin, )
    
    def list(self, request, *args, **kwargs):
        third_field = choose_lang(request)
        
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, fields={"en_name","id", "parent", third_field}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        third_field = choose_lang(request)
        
        instance = self.get_object()
        serializer = self.get_serializer(instance, fields={"id", "parent", third_field})
        return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def category_locations_filter(request: HttpRequest, category_id: int):
    locations = ServiceProviderLocations.objects.filter(Q(service_provider__category=category_id))
    
    serializer = LocationSerializerSafe(locations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

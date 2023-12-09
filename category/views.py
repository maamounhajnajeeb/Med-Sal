from rest_framework import viewsets, decorators
from rest_framework import permissions, status
from rest_framework.response import Response

from django.http import HttpRequest

from .serializers import CategorySerializer
from .helpers import searching_func
from .permissions import IsAdmin
from .models import Category

from service_providers.serializers import LocationSerializerSafe
from service_providers.models import ServiceProviderLocations
from notification.models import Notification



@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def parent_sub_category(request, pk: int):
    third_field = request.META.get("Accept-Language")
    
    queryset = Category.objects.filter(parent=pk)
    serializer = CategorySerializer(queryset, fields={"id", "parent", f"{third_field}_name"}, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def prime_categories(request):
    third_field = request.META.get("Accept-Language")
    
    queryset = Category.objects.filter(parent=None)
    serializer = CategorySerializer(queryset, fields={"id", "parent", f"{third_field}_name"}, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def search_category(request: HttpRequest):
    third_field = request.META.get("Accept-Language")
    queryset = searching_func(request, third_field)
    
    if not queryset.exists():
        return Response({
            "message": "There is not result with this search key"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CategorySerializer(queryset, fields={"id", "parent", f"{third_field}_name"}, many=True)
    
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
        third_field = request.META.get("Accept-Language")
        
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, fields={"id", "parent", f"{third_field}_name"}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        third_field = request.META.get("Accept-Language")
        
        instance = self.get_object()
        serializer = self.get_serializer(instance, fields={"id", "parent", f"{third_field}_name"})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="System"
            , en_content=f"{resp.data['en_name']} category added"
            , ar_content=f" تمت إضافة {resp.data['ar_name']}")
        
        return Response(resp.data, status=resp.status_code)
    
    def perform_destroy(self, instance: Category):
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=self.request.user.email, receiver_type="System"
            , en_content=f"{instance.en_name} category deleted"
            , ar_content=f" تم حذف {instance.ar_name}")
        
        return super().perform_destroy(instance)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def category_locations_filter(request: HttpRequest, category_id: int):
    locations = ServiceProviderLocations.objects.filter(service_provider__category=category_id)
    
    serializer = LocationSerializerSafe(locations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

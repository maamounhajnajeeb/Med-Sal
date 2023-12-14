from rest_framework import generics, decorators
from rest_framework.response import Response
from rest_framework import status

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.http import HttpRequest

from collections import defaultdict
from typing import Any

from services import models, serializers, helpers

from products.file_handler import UploadImages, DeleteFiles
from notification.models import Notification
from utils.permission import HasPermission



class CreateService(generics.CreateAPIView, helpers.FileMixin):
    serializer_class = serializers.CreateServicesSerializer
    permission_classes = (HasPermission, )
    queryset = models.Service.objects
    
    def get_permissions(self):
        return [permission("service") for permission in self.permission_classes]
    
    def create(self, request: HttpRequest, *args, **kwargs):
        image_objs = request.FILES.getlist("image")
        upload_images = UploadImages(request)
        images_names = upload_images.upload_files("services", image_objs)
        
        request.data["image"] = images_names
        resp = super().create(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="system", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , ar_content="تم إضافة خدمة جديدة إلى خدماتك"
            , en_content="A new service added to your sevices")
        
        return Response(resp.data, status=resp.status_code)


class ServiceRUD(generics.RetrieveUpdateDestroyAPIView, helpers.FileMixin):
    serializer_class = serializers.RUDServicesSerializer
    permission_classes = (HasPermission, )
    queryset = models.Service.objects
    
    def get_permissions(self):
        return [permission("service") for permission in self.permission_classes]
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs["language"] = language
        return super().get_serializer(*args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance, ], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def perform_destroy(self, instance):
        delete_files = DeleteFiles()
        delete_files.delete_files(instance.image)
        
        Notification.objects.create(
            sender="system", sender_type="System"
            , receiver=self.request.user.email, receiver_type="Service_Provider"
            , ar_content="تم حذف الخدمة"
            , en_content="service has been deleted")
        
        return super().perform_destroy(instance)
    
    def update(self, request: HttpRequest, *args, **kwargs):
        data = request.data
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        if request.data.get("image"):
            image_objs = request.FILES.getlist("image")
            upload_images = UploadImages(request)
            images_names = upload_images.upload_files("services", image_objs)
            
            request.data["image"] = images_names
            
            delete_files = DeleteFiles()
            delete_files.delete_files(instance.image)
            
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        Notification.objects.create(
            sender="system", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , ar_content="تم تعديل الخدمة"
            , en_content="service has been updated")
        
        return Response(serializer.data)

#
class ListAllServices(generics.ListAPIView):
    serializer_class = serializers.RUDServicesSerializer
    queryset = models.Service.objects
    permission_classes = ( )
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs["language"] = language
        return super().get_serializer(*args, **kwargs)

#
@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def provider_services(request: HttpRequest, provider_id: int):
    """
    return services for specific provider
    """
    provider_id = provider_id or request.user.id
    language = request.META.get("Accept-Language")
    queryset = models.Service.objects.filter(provider_location__service_provider=provider_id)
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

# 
@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def provider_services_by_category(request: HttpRequest, provider_id: int):
    """
    return services number for each category in a service_provider
    """
    language = request.META.get("Accept-Language")
    queryset = models.Service.objects.filter(provider_location__service_provider=provider_id)
    
    def aggregate_queryset(queryset):
        frequencies = defaultdict(int)
        for query in queryset:
            category_id = query.category.id
            category_name = query.category.en_name if language == "en" else query.category.ar_name 
            
            frequencies[(category_id, category_name)] += 1
        return frequencies
    
    def serialize_data(frequencies: defaultdict[tuple[int, str], int]):
        data = []
        for k, v in frequencies.items():
            data.append({"category_id": k[0], "category_name": k[1], "services_count": v})
        
        return data
    
    frequencies = aggregate_queryset(queryset)
    data = serialize_data(frequencies)
    
    return Response(data, status=status.HTTP_200_OK)

#
@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def provider_category_services(request: HttpRequest, provider_id: int, category_id: int):
    """
    return category related services for a specific provider
    """
    language = request.META.get("Accept-Language")
    queryset = models.Service.objects.filter(
        provider_location__service_provider=provider_id, category=category_id)
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

#
@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def category_services_by_name(request: HttpRequest, category_name: str):
    """
    return services for specific category by category name
    """
    language = request.META.get("Accept-Language")
    queryset = helpers.searching_func(category_name)
    
    if not queryset.exists():
        return Response({"message": "No services found relates to this category"}
                    , status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def service_price_range(request: HttpRequest):
    """
    return services depending on price range
    """
    language = request.META.get("Accept-Language")
    min_price, max_price = int(request.query_params["min_price"]), int(request.query_params["max_price"])
    
    queryset = models.Service.objects.filter(price__range=(min_price, max_price))
    if not queryset.exists():
        return Response({
            "message": "No services found within this range"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def multiple_filters(request: HttpRequest):
    """
    return services depending on specified filters
    filters set : {rate, category_name, (min_price, max_price), (longitude, latitude)}
    """
    language = request.META.get("Accept-Language")
    params = {}
    callables = (check_rate, check_range, check_category)
    for function in callables:
        params = function(request, params, language=language)
    
    queryset = check_distance(request, params)
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


def check_distance(request: HttpRequest, params: dict[str, Any], **kwargs):
    """
    helper function for multiple filters api function
    """
    longitude, latitude = request.query_params.get("longitude"), request.query_params.get("latitude")
    if longitude and latitude:
        longitude, latitude = float(longitude), float(latitude)
        location = Point(longitude, latitude)
        params["service_provider_location__location__distance_lt"] = (location, 1000000)
    
        queryset = models.Service.objects.filter(
            **params).annotate(
                distance=Distance("service_provider_location__location", location)).order_by("distance")
    
    queryset = models.Service.objects.filter(**params)
    return queryset

def check_category(request: HttpRequest, params: dict[str, Any], **kwargs):
    """
    helper function for multiple filters api function
    """
    category_name = request.query_params.get("category_name")
    if category_name:
        q_exp = f"category__{kwargs.get('language')}_name__icontains"
        params[q_exp] = str(category_name)
    
    return params

def check_range(request: HttpRequest, params: dict[str, Any], **kwargs):
    """
    helper function for multiple filters api function
    """
    min_price, max_price = request.query_params.get("min_price"), request.query_params.get("max_price")
    if min_price and max_price:
        min_price, max_price = float(min_price), float(max_price)
        params["price__range"] = (min_price, max_price)
    
    return params

def check_rate(request: HttpRequest, params: dict[str, Any], **kwargs):
    """
    helper function for multiple filters api function
    """
    rate = request.query_params.get("rate")
    if rate:
        rate = int(rate)
        params["service_rates__rate"] = rate
    
    return params

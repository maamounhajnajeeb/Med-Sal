from rest_framework import generics, decorators
from rest_framework.response import Response
from rest_framework import status

from django.contrib.gis.db.models.functions import Distance
from django.db.models import Count, Avg, Min, Max, Sum
from django.contrib.gis.geos import Point
from django.db.models import Q, Avg
from django.http import HttpRequest

from collections import defaultdict
from functools import reduce
from typing import Any

from services import models, serializers, helpers

from products.file_handler import UploadImages, DeleteFiles
from notification.models import Notification
from category.models import Category

from utils.permission import HasPermission
from utils.catch_helper import catch


#
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

#
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
def provider_services(request: HttpRequest, provider_id: int= None):
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
    # all_cat = Category.objects.annotate(num_of_services=Count("services", filter=Q(services__gt=1)))
    # for cat in all_cat: cat.id, cat.ar_name, cat.en_name, cat.num_services
    """
    number of services for each categories available in specific provider
    returns {category_id, category_name, services_count}
    """
    language = request.META.get("Accept-Language")
    queryset = models.Service.objects.filter(provider_location__service_provider=provider_id)
    prices = queryset.aggregate(min_price=Min("price"), max_price=Max("price"))
    
    def categories(queryset):
        frequencies = defaultdict(int)
        for query in queryset:
            category_id = query.category.id
            category_name = query.category.en_name if language == "en" else query.category.ar_name 
            
            frequencies[(category_id, category_name)] += 1
            
        def serialize_data(frequencies: defaultdict[tuple[int, str], int]):
            data = []
            for k, v in frequencies.items():
                data.append({"category_id": k[0], "category_name": k[1], "services_count": v})
            
            return data
        
        return serialize_data(frequencies)
    
    def sizing_rates():
        # first we filtered the provider services
        # then we aggregate similar services and find it's average rate
        queryset = models.ServiceRates.objects.filter(
        service__provider_location__service_provider=provider_id).values(
            "service").annotate(avg_rate=Avg("rate"))
        
        limits = { (4.5, 5): 5, (3.5, 4.5): 4, (2.5, 3.5): 3, (1.5, 2.5): 2, (0.5, 1.5): 1, (0, 0.5): 0 }
        rates = defaultdict(int)
        
        for query in queryset:
            for limit in limits:
                if query["avg_rate"] >= limit[0] and query["avg_rate"] < limit[1]:
                    rates[limits[limit]] += 1
                    break
        
        return rates
    
    data = {}
    
    data["prices"] = {"min_price": prices["min_price"], "max_price": prices["max_price"]}
    data["categories"] = categories(queryset)
    data["rates"] = sizing_rates()
    
    return Response(data, status=status.HTTP_200_OK)


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

#
@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def multiple_filters(request: HttpRequest):
    """
    return services depending on specified filters
    filters set : {rates, categories, (min_price, max_price), (longitude, latitude)}
    """
    params = request.query_params
    
    q_expressions = set()
    callables = (check_range, check_category)
    for function in callables:
        q_expressions.add(function(params))
    
    q_expressions.discard(None)
    
    queryset = check_distance(params=params, q_expressions=q_expressions)
    queryset = check_rate(params, queryset)
    print(queryset.count())
    
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=request.META.get("Accept-Language"))
    return Response(serializer.data, status=status.HTTP_200_OK)


def check_distance(params: dict[str, None], q_expressions: set):
    """
    helper function for multiple filters api function
    """
    longitude, latitude = params.get("longitude", None), params.get("latitude", None)
    if longitude and latitude:
        longitude, latitude = float(longitude), float(latitude)
        location = Point(longitude, latitude)
        q_exp=Q(service_provider_location__location__distance_lt=(location, 1000000))
        
        queryset = models.Service.objects.filter(
            q_exp, *q_expressions).annotate(
                distance=Distance("service_provider_location__location", location)).order_by("distance")
    
    else:
        queryset = models.Service.objects.filter(*q_expressions)
    
    return queryset

def check_category(params: dict[str, Any]):
    """
    helper function for multiple filters api function
    """
    q_exp = None
    category_ids = params.get("categories", None)
    if category_ids:
        new_category_ids = catch(category_ids)
        
        q_exp = (Q(category__id=int(x)) for x in new_category_ids)
        q_exp = reduce(lambda a, b: a | b, q_exp)
    
    return q_exp

def check_range(params: dict[str, Any]):
    """
    helper function for multiple filters api function
    """
    q_exp = None
    min_price, max_price = params.get("min_price", None), params.get("max_price", None)
    if min_price and max_price:
        min_price, max_price = float(min_price), float(max_price)
        q_exp = Q(price__range=(min_price, max_price))
    
    return q_exp

def check_rate(params: dict[str, None], services_queryset):
    """
    helper function for multiple filters api function
    """
    rates = params.get("rates", None)
    if not rates:
        return services_queryset
    
    rates = catch(rates)
    
    new_services = []
    for service in services_queryset:
        avg_service_rate = service.service_rates.aggregate(Avg("rate", default=0))["rate__avg"]
        for rate in rates:
            if rate-0.5 <= avg_service_rate <= rate+0.5:
                new_services.append(service)
                break
    
    return new_services

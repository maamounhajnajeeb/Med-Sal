from rest_framework import decorators, generics
from rest_framework import permissions, status
from rest_framework.response import Response

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.http import HttpRequest

from products import permissions as local_permissions
from products import models, serializers, helpers
from products.file_handler import UploadImages, DeleteFiles

from typing import Any

from notification.models import Notification



class AllProducts(generics.ListAPIView):
    """
        An api that lists all products
    """
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def list(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, fields={"language": language})
        return Response(serializer.data)


class CreateProduct(generics.CreateAPIView):
    """
        An api that allows to add products 
    """
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def create(self, request, *args, **kwargs):
        new_file_names = self._upload_images(request)
        request.data["images"] = new_file_names
        resp = super().create(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , en_content="a new product added to your specified location"
            , ar_content="تم إضافة منتج جديد للفرع المحدد")
        
        return Response(resp.data, status=resp.status_code)
    
    def _upload_images(self, request):
        file_manager = UploadImages(request)
        return file_manager.upload_files("products", request.FILES.getlist("images"))


class RUDProduct(generics.RetrieveUpdateDestroyAPIView):
    """
        An api that allows to Read, Update and Delete a specific product 
        product ID is required 
    """
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def retrieve(self, request, *args, **kwargs):
        lanuage = request.META.get("Accept-Language")
        
        instance = self.get_object()
        serializer = self.get_serializer([instance], many=True, fields={"language": lanuage})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        data = request.data.copy()
        if request.data.get("images"):
            # first delete old ones
            DeleteFiles().delete_files(instance.images)
            # then upload new ones and change names
            file_manager = UploadImages(request)
            data["images"] = file_manager.upload_files("products", request.FILES.getlist("images"))
            
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , en_content="product information edited"
            , ar_content="تم تعديل معلومات المنتج")
        
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        DeleteFiles().delete_files(instance.images)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=self.request.user.email, receiver_type="Service_Provider"
            , en_content="the product deleted"
            , ar_content="تم حذف المنتج")
        
        instance.delete()


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_category(request: HttpRequest, pk: int):
    """
    get all products for specific category
    pk here is category_id
    for everybody
    """
    queryset = models.Product.objects.filter(service_provider_location__service_provider__category=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_location(request: HttpRequest, pk: int):
    """
    get all products for specific location
    pk here is location_id
    for everybody
    """
    queryset = models.Product.objects.filter(service_provider_location=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_provider(request: HttpRequest, pk: int):
    """
    get all products for specific service provider
    pk here is service_provider_id
    for everybody
    """
    queryset = models.Product.objects.filter(service_provider_location__service_provider=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def category_products_by_name(request: HttpRequest, category_name: str):
    language = request.META.get("Accept-Language")
    queryset = helpers.searching_func(category_name, language)
    
    if not queryset.exists():
        return Response({"message": "No products found relates to this category name"}
                    , status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.ProudctSerializer(queryset, many=True, fields={"language": language})
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def products_price_range(request: HttpRequest):
    language = request.META.get("Accept-Language")
    min_price, max_price = int(request.query_params["min_price"]), int(request.query_params["max_price"])
    
    queryset = models.Product.objects.filter(price__range=(min_price, max_price))
    if not queryset.exists():
        return Response({
            "message": "No products found within this range"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.ProudctSerializer(queryset, many=True, fields={"language":language})
    return Response(serializer.data, status=status.HTTP_200_OK)



@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def multiple_filters(request: HttpRequest):
    """
    multiple filters helper function
    """
    language = request.META.get("Accept-Language")
    params = {}
    
    callables = (check_rate, check_range, check_category)
    for func in callables:
        params = func(request, params, language=language)
    
    queryset = check_distance(request, params)
    
    serializer = serializers.ProudctSerializer(queryset, many=True, fields={"language": language})
    return Response(serializer.data, status=status.HTTP_200_OK)


def check_distance(request: HttpRequest, params: dict[str, Any], **kwargs):
    longitude, latitude = request.query_params.get("logitude"), request.query_params.get("latitude")
    if longitude and latitude:
        longitude, latitude = float(longitude), float(latitude)
        location = Point(longitude, latitude)
        params["service_provider_location__location__distance_lt"] = (location, 1000000)
    
        queryset = models.Product.objects.filter(
            **params).annotate(
                distance=Distance("service_provider_location__location", location)).order_by("distance")
    
    queryset = models.Product.objects.filter(**params)
    
    return queryset

def check_category(request: HttpRequest, params: dict[str, Any], **kwargs) -> dict[str, Any]:
    """
    multiple filters helper function
    """
    category_name = request.query_params.get("category_name")
    if category_name:
        category_name = str(category_name)
        q = "service_provider_location__service_provider__category__en_name__icontains"
        if kwargs.get("language") == "ar":
            q = "service_provider_location__service_provider__category__ar_name__icontains"
        params[q] = category_name
    
    return params

def check_range(request: HttpRequest, params: dict[str, Any], **kwargs) -> dict[str, Any]:
    """
    multiple filters helper function
    """
    min_price, max_price = request.query_params.get("min_price"), request.query_params.get("max_price")
    if min_price and max_price:
        min_price, max_price = float(min_price), float(max_price)
        params["price__range"] = (min_price, max_price)
    
    return params

def check_rate(request, params: dict[str, Any], **kwargs) -> dict[str, Any]:
    """
    multiple filters helper function
    """
    # maybe we need a .distinct() function in the future because of reverse relationship
    rate = int(request.query_params.get("rate"))
    if rate:
        params["product_rates__rate"] = rate
    
    return params

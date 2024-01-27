from rest_framework import decorators, generics
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.request import Request

from django.contrib.postgres.search import SearchVector, SearchQuery
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import Q, Avg, QuerySet
from django.contrib.gis.geos import Point

from functools import reduce
from typing import Any

from products.file_handler import UploadImages, DeleteFiles
from products import permissions as local_permissions
from products import models, serializers

from core.pagination_classes.nine_element_paginator import custom_pagination_function
from notification.models import Notification
from utils.catch_helper import catch



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
        serializer = self.get_serializer(queryset, many=True, language=language)
        return Response(serializer.data)


class CreateProduct(generics.CreateAPIView):
    """
        An api that allows to add products 
    """
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def create(self, request: Request, *args, **kwargs):
        if not request.FILES.getlist("images"):
            return Response({"Error": "we need at least one image for each product"},
                    status=status.HTTP_400_BAD_REQUEST)
        
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
        language = request.META.get("Accept-Language")
        
        instance = self.get_object()
        serializer = self.get_serializer([instance], many=True, language=language)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        data = request.data.copy()
        if request.data.get("images"):
            # first delete old ones
            DeleteFiles().delete_files(instance.images)
            # then upload new ones and change names
            file_manager = UploadImages(request)
            data["images"] = file_manager.upload_files("products", request.FILES.getlist("images"))
            
        serializer = self.get_serializer(instance, data=data, partial=partial, language=language)
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
def products_by_category(request: Request, pk: int):
    """
    get all products for specific category
    pk here is category_id
    for everybody
    """
    language = request.META.get("Accept-Language")
    queryset = models.Product.objects.filter(service_provider_location__service_provider__category=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_location(request: Request, pk: int):
    """
    get all products for specific location
    pk here is location_id
    for everybody
    """
    language = request.META.get("Accept-Language")
    queryset = models.Product.objects.filter(service_provider_location=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_provider(request: Request, pk: int):
    """
    get all products for specific service provider
    pk here is service_provider_id
    for everybody
    """
    language = request.META.get("Accept-Language")
    queryset = models.Product.objects.filter(service_provider_location__service_provider=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def category_products_by_name(request: Request, category_name: str):
    language = request.META.get("Accept-Language")
    main_q = "service_provider_location__service_provider__category__"
    
    search_terms = category_name.split("_")
    search_exprs = (Q(search=SearchQuery(word)) for word in search_terms)
    search_func = reduce(lambda x, y: x | y, search_exprs)
    
    queryset = models.Product.objects.annotate(
        search=SearchVector(f"{main_q}en_name", f"{main_q}ar_name")).filter(search_func)
    
    if not queryset.exists():
        return Response({"message": "No products found relates to this category name"}
                    , status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.ProudctSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def products_price_range(request: Request):
    language = request.META.get("Accept-Language")
    min_price, max_price = int(request.query_params["min_price"]), int(request.query_params["max_price"])
    
    queryset = models.Product.objects.filter(price__range=(min_price, max_price))
    if not queryset.exists():
        return Response({
            "message": "No products found within this range"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.ProudctSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


def check_category(query_params: dict[str, Any], products_queryset: QuerySet):
    """
    helper function for multiple filters api function
    """
    category_ids = query_params.get("categories", None)
    new_category_ids = catch(category_ids)
    
    services_q_expr = (
        Q(service_provider_location__service_provider__category__id=int(x)) for x in new_category_ids)
    services_q_expr = reduce(lambda a, b: a | b, services_q_expr)
    
    return services_q_expr, products_queryset

def check_range(query_params: dict[str, Any], products_queryset: QuerySet):
    """
    helper function for multiple filters api function
    """
    min_price, max_price = query_params.get("range")[0][0], query_params.get("range")[1][0]
    min_price, max_price = float(min_price), float(max_price)
    q_expr = Q(price__range=(min_price, max_price))
    
    return q_expr, products_queryset

def search_func(query_params: dict[str, Any], products_queryset: QuerySet):
    words: str = query_params.get("search").split("_")
    q_exprs = (Q(search=SearchQuery(word)) for word in words)
    q_func = reduce(lambda x, y: x | y, q_exprs)
    
    products_queryset = products_queryset.annotate(search=SearchVector("en_title", "ar_title"))
    
    return q_func, products_queryset

def check_rate(query_params: dict[str, Any], products_queryset: QuerySet):
    rates = catch(query_params.get("rates"))
    
    products_queryset = products_queryset.prefetch_related("product_rates")
    products_queryset = products_queryset.annotate(avg_rate=Avg("product_rates__rate"))
    
    q_expr = (Q(avg_rate__gt=rate-0.5) & Q(avg_rate__lte=rate+0.5) for rate in rates)
    q_expr = reduce(lambda x, y: x | y, q_expr)
    
    return q_expr, products_queryset

def check_distance(query_params: dict[str, Any], products_queryset: QuerySet):
    location = Point(query_params.get("distance"), srid=4326)
    
    products_q_expr = Q(service_provider_location__location__distance_lte=(location, D(km=10)))
    products_queryset = products_queryset.annotate(
        distance=Distance("service_provider_location__location", location)).order_by("distance")
    
    return products_q_expr, products_queryset

def get_pagination(pagination_number: int):
    a = pagination_number // 2
    b = pagination_number - a
    return a, b

def get_callables(query_params: dict[str, Any]):
    new_query_params = query_params.copy()
    
    # taking care of pagination number
    pagination_number = new_query_params.pop("pagination_number", None)
    if pagination_number is None:
        pagination_number = 9
    else:
        pagination_number = int(pagination_number[0])
    
    # switching longitude and latitude to distance within query_params
    if new_query_params.get("longitude") and new_query_params.get("latitude"):
        longitude, latitude = new_query_params.pop("longitude")[0], new_query_params.pop("latitude")[0]
        new_query_params["distance"] = float(longitude), float(latitude)
    
    # switching min_price and max_price to price__range within query_params
    if new_query_params.get("min_price") and new_query_params.get("max_price"):
        min_price, max_price = new_query_params.pop("min_price"), new_query_params.pop("max_price")
        new_query_params["range"] = min_price, max_price
    
    callables_hashtable = {
        "distance": check_distance, "search": search_func,
        "rates": check_rate, "range": check_range,
        "categories": check_category
    }
    
    callables = [callables_hashtable[key] for key in new_query_params.keys()]
    return callables, new_query_params, pagination_number


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def search_in_provider_products(request: Request, provider_id: int):
    # first we get the language and query_params, then we make main querysets
    language, query_params = request.META.get("Accept-Language"), request.query_params
    products_main_queryset = models.Product.objects
    
    # then we get the callabels which mapped with the served query_params, and take care of pagination num
    callables, query_params, pagination_number = get_callables(query_params)
    
    # then we prepare the Q_exprs that will filter the querysets
    # we stand on callabels and query_params from the last step
    services_Q_exprs = set()
    for func in callables:
        services_Q_expr, products_main_queryset = func(query_params, products_main_queryset)
        services_Q_exprs.add(services_Q_expr)
    
    # here we apply filtering (if exists) on the querysets
    products_main_queryset = products_main_queryset.filter(
        service_provider_location__service_provider=provider_id ,*services_Q_exprs)
    
    # paginate the queryset under the client-side rules
    services_paginator = custom_pagination_function(pagination_number)
    paginated_services = services_paginator.paginate_queryset(products_main_queryset, request)
    
    # serializing the queryset data
    serialized_services = serializers.ProudctSerializer(paginated_services, many=True, language=language)
    
    return Response(data=serialized_services.data, status=status.HTTP_200_OK)


@decorators.api_view(["POST", ])
@decorators.permission_classes([permissions.IsAdminUser, ])
def activation_switcher(req: Request, pk: int):
    product_obj = models.Product.objects.filter(id=pk)
    if not product_obj.exists():
        return Response(
            {"Error": "Product objects with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    activation_status = req.data.get("status")
    if activation_status:
        activation_status = False if activation_status == "false" else True
        product_obj = product_obj.first()
        product_obj.is_active = activation_status
        product_obj.save()
        
        return Response(
            {"Message": f"Activation status changed to {activation_status} for product with id: {pk}"},
            status=status.HTTP_201_CREATED)
    
    return Response(
        {"Error": "We need status attr to detect activation action to the product object"},
        status=status.HTTP_400_BAD_REQUEST)

from rest_framework import decorators, status
from rest_framework.response import Response

from django.contrib.postgres.search import SearchVector, SearchQuery
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.http import HttpRequest
from django.db.models import Q, Avg

from functools import reduce
from itertools import chain
from typing import Any

from core.pagination_classes.nine_element_paginator import CustomPagination

from services.serializers import RUDServicesSerializer
from products.serializers import ProudctSerializer
from products.models import Product
from services.models import Service
from utils.catch_helper import catch


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def language_switcher(request: HttpRequest):
    return Response({"message": "language switched successfully"}, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def search_in_services_products(request: HttpRequest):
    language, search = request.META.get("Accept-Language"), request.data.get("search").replace("_", " ")
    
    service_queryset = Service.objects.annotate(
        search=SearchVector("en_title", "ar_title")).filter(search=SearchQuery(search))
    
    product_queryset = Product.objects.annotate(
        search=SearchVector("en_title", "ar_title")).filter(search=SearchQuery(search))
    
    service_serializer = RUDServicesSerializer(service_queryset, many=True, language=language)
    product_serialzier = ProudctSerializer(product_queryset, many=True, language=language)
    concatenated_queryset = list(chain(service_serializer.data, product_serialzier.data))
    
    return Response(data=concatenated_queryset, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def multiple_filters(request: HttpRequest):
    """
    query_params = {rates: list[numbers], min_price: number, max_price: number
                    , categories: list[numbers], }
    """
    language = request.META.get("Accept-Language")
    params = request.query_params
    
    q_expressions = set()
    callables = (check_range, check_category)
    for func in callables:
        q_expressions.add(func(params))
    
    q_expressions.discard(None)
    
    q_expressions, queryset = check_distance(params=params, q_expressions=q_expressions)
    queryset = check_rate(params, queryset)
    
    paginator = CustomPagination()
    list_products = paginator.paginate_queryset(queryset, request)
    
    serializer = ProudctSerializer(list_products, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


def check_distance(params: dict[str, Any], q_expressions: set):
    longitude, latitude = params.get("logitude"), params.get("latitude")
    if longitude and latitude:
        longitude, latitude = float(longitude), float(latitude)
        location = Point(longitude, latitude)
        q_exp=Q(service_provider_location__location__distance_lt=(location, 1000000))
        q_expressions.add(q_exp)
        
        queryset = Product.objects.annotate(
            distance=Distance("service_provider_location__location", location)
                ).order_by("distance")
    
    else:
        queryset = Product.objects
    
    return q_expressions, queryset

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

def check_rate(params: dict[str, None], products_queryset):
    """
    helper function for multiple filters api function
    """
    rates = params.get("rates", None)
    if not rates:
        return products_queryset
    
    rates = catch(rates)
    
    new_products = []
    for product in products_queryset:
        avg_product_rate = product.product_rates.aggregate(Avg("rate", default=0))["rate__avg"]
        for rate in rates:
            if rate-0.5 <= avg_product_rate <= rate+0.5:
                new_products.append(product)
                break
    
    return new_products

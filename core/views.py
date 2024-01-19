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


def get_callables(query_params):
    if query_params.get("longitude") and query_params.get("latitude"):
        longitude, latitude = query_params.pop("longitude"), query_params.pop("latitude")
        query_params["distance"] = longitude, latitude
    
    if query_params.get("min_price") and query_params.get("max_price"):
        min_price, max_price = query_params.get("min_price"), query_params.get("max_price")
        query_params["range"] = min_price, max_price
    
    callables_hashtable = {
        "distance": check_distance,"rate": check_rate,"range": check_range,
        "category": check_category, "search": "", "paginage": ""
    }
    
    callables = [callables_hashtable[key] for key in query_params.keys()]
    return callables, query_params


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def search_in_services_products(request: HttpRequest):
    language, query_params = request.META.get("Accept-Language"), request.query_params
    callables, query_params = get_callables(query_params)
    
    Q_exprs = set()
    for func in callables:
        Q_exprs.add(func(query_params, Q_exprs))
    
    # service_queryset = Service.objects.annotate(
    #     search=SearchVector("en_title", "ar_title")).filter(search=SearchQuery(search))
    
    # product_queryset = Product.objects.annotate(
    #     search=SearchVector("en_title", "ar_title")).filter(search=SearchQuery(search))
    
    # service_serializer = RUDServicesSerializer(service_queryset, many=True, language=language)
    # product_serialzier = ProudctSerializer(product_queryset, many=True, language=language)
    # concatenated_queryset = list(chain(service_serializer.data, product_serialzier.data))
    
    # return Response(data=concatenated_queryset, status=status.HTTP_200_OK)
    
    return Response({"message": "hi"}, status=status.HTTP_200_OK)


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

def check_category(query_params: dict[str, Any], Q_exprs: set):
    """
    helper function for multiple filters api function
    """
    category_ids = query_params.get("categories", None)
    new_category_ids = catch(category_ids)
    
    q_expr = (Q(category__id=int(x)) for x in new_category_ids)
    q_expr = reduce(lambda a, b: a | b, q_expr)
    
    return q_expr

def check_range(query_params: dict[str, Any], Q_exprs: set):
    """
    helper function for multiple filters api function
    """
    min_price, max_price = query_params.get("range")[0], query_params.get("range")[1]
    min_price, max_price = float(min_price), float(max_price)
    q_expr = Q(price__range=(min_price, max_price))
    
    return q_expr

def check_rate(params: dict[str, None], products_queryset):
    """
    helper function for multiple filters api function
    """
    rates = params.get("rates", None)
    
    rates = catch(rates)
    
    new_products = []
    for product in products_queryset:
        avg_product_rate = product.product_rates.aggregate(Avg("rate", default=0))["rate__avg"]
        for rate in rates:
            if rate-0.5 <= avg_product_rate <= rate+0.5:
                new_products.append(product)
                break
    
    return new_products

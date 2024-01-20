from rest_framework import decorators, status
from rest_framework.response import Response

from django.contrib.postgres.search import SearchVector, SearchQuery
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q, Avg, QuerySet
from django.contrib.gis.geos import Point
from django.http import HttpRequest

from functools import reduce
from itertools import chain
from typing import Any

from core.pagination_classes.nine_element_paginator import custom_pagination_function

from services.serializers import RUDServicesSerializer
from products.serializers import ProudctSerializer
from products.models import Product
from services.models import Service
from utils.catch_helper import catch


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def language_switcher(request: HttpRequest):
    return Response({"message": "language switched successfully"}, status=status.HTTP_200_OK)


def check_category(query_params: dict[str, Any], services_queryset: QuerySet, products_queryset: QuerySet):
    """
    helper function for multiple filters api function
    """
    category_ids = query_params.get("categories", None)
    new_category_ids = catch(category_ids)
    
    services_q_expr = (Q(category__id=int(x)) for x in new_category_ids)
    services_q_expr = reduce(lambda a, b: a | b, services_q_expr)
    
    products_q_expr = (
        Q(service_provider_location__service_provider__category__id=int(x)) for x in new_category_ids)
    products_q_expr = reduce(lambda x, y: x | y, products_q_expr)
    
    return services_q_expr, products_q_expr, services_queryset, products_queryset

def check_range(query_params: dict[str, Any], services_queryset: QuerySet, products_queryset: QuerySet):
    """
    helper function for multiple filters api function
    """
    min_price, max_price = query_params.get("range")[0][0], query_params.get("range")[1][0]
    min_price, max_price = float(min_price), float(max_price)
    q_expr = Q(price__range=(min_price, max_price))
    
    return q_expr, q_expr, services_queryset, products_queryset

def search_func(query_params: dict[str, Any], services_queryset: QuerySet, products_queryset: QuerySet):
    words: str = query_params.get("search").replace("_", " ")
    q_expr = Q(search=SearchQuery(words))
    
    services_queryset = services_queryset.annotate(search=SearchVector("en_title", "ar_title"))
    products_queryset = products_queryset.annotate(search=SearchVector("en_title", "ar_title"))
    
    return q_expr, q_expr, services_queryset, products_queryset

def check_rate(query_params: dict[str, Any], services_queryset: QuerySet, products_queryset: QuerySet):
    rates = catch(query_params.get("rates"))
    
    services_queryset = services_queryset.prefetch_related("service_rates")
    services_queryset = services_queryset.annotate(avg_rate=Avg("service_rates__rate"))
    
    products_queryset = products_queryset.prefetch_related("product_rates")
    products_queryset = products_queryset.annotate(avg_rate=Avg("product_rates__rate"))
    
    q_expr = (Q(avg_rate__gt=rate-0.5) & Q(avg_rate__lte=rate+0.5) for rate in rates)
    q_expr = reduce(lambda x, y: x | y, q_expr)
    
    return q_expr, q_expr, services_queryset, products_queryset

def get_callables(query_params: dict[str, Any]):
    new_query_params = query_params.copy()
    if new_query_params.get("longitude") and new_query_params.get("latitude"):
        longitude, latitude = new_query_params.pop("longitude"), new_query_params.pop("latitude")
        new_query_params["distance"] = longitude, latitude
    
    if new_query_params.get("min_price") and new_query_params.get("max_price"):
        min_price, max_price = new_query_params.pop("min_price"), new_query_params.pop("max_price")
        new_query_params["range"] = min_price, max_price
    
    callables_hashtable = {
        # "distance": check_distance,
        "rates": check_rate,"range": check_range,
        "categories": check_category, "search": search_func
        # , "paginage": ""
    }
    
    callables = [callables_hashtable[key] for key in new_query_params.keys()]
    return callables, new_query_params


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def search_in_services_products(request: HttpRequest):
    language, query_params = request.META.get("Accept-Language"), request.query_params
    services_main_queryset, products_main_queryset = Service.objects, Product.objects
    callables, query_params = get_callables(query_params)
    
    services_Q_exprs, products_Q_exprs = set(), set()
    for func in callables:
        services_Q_expr, products_Q_expr, services_main_queryset, products_main_queryset = func(
            query_params, services_main_queryset, products_main_queryset)
        services_Q_exprs.add(services_Q_expr)
        products_Q_exprs.add(products_Q_expr)
    
    services_main_queryset = services_main_queryset.filter(*services_Q_exprs)
    products_main_queryset = products_main_queryset.filter(*products_Q_exprs)
    
    services_paginator = custom_pagination_function(4)
    paginated_services = services_paginator.paginate_queryset(services_main_queryset, request)
    products_paginator = custom_pagination_function(5)
    paginated_products = products_paginator.paginate_queryset(products_main_queryset, request)
    
    serialized_services = RUDServicesSerializer(paginated_services, many=True, language=language)
    serialized_products = ProudctSerializer(paginated_products, many=True, language=language)
    
    return Response(data=serialized_services.data + serialized_products.data, status=status.HTTP_200_OK)

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

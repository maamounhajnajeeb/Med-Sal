from rest_framework import decorators, status
from rest_framework.response import Response
from rest_framework.request import Request

from django.contrib.postgres.search import SearchVector, SearchQuery
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q, Avg, QuerySet, Max, Min
from django.contrib.gis.geos import Point

from collections import defaultdict
from functools import reduce
from typing import Any

from core.pagination_classes.nine_element_paginator import custom_pagination_function

from services.serializers import RUDServicesSerializer
from products.serializers import ProudctSerializer
from products.models import Product
from services.models import Service
from utils.catch_helper import catch


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def language_switcher(request: Request):
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
    words: str = query_params.get("search").split("_")
    q_exprs = (Q(search=SearchQuery(word)) for word in words)
    q_func = reduce(lambda x, y: x | y, q_exprs)
    
    services_queryset = services_queryset.annotate(search=SearchVector("en_title", "ar_title"))
    products_queryset = products_queryset.annotate(search=SearchVector("en_title", "ar_title"))
    
    return q_func, q_func, services_queryset, products_queryset

def check_rate(query_params: dict[str, Any], services_queryset: QuerySet, products_queryset: QuerySet):
    rates = catch(query_params.get("rates"))
    
    services_queryset = services_queryset.prefetch_related("service_rates")
    services_queryset = services_queryset.annotate(avg_rate=Avg("service_rates__rate"))
    
    products_queryset = products_queryset.prefetch_related("product_rates")
    products_queryset = products_queryset.annotate(avg_rate=Avg("product_rates__rate"))
    
    q_expr = (Q(avg_rate__gt=rate-0.5) & Q(avg_rate__lte=rate+0.5) for rate in rates)
    q_expr = reduce(lambda x, y: x | y, q_expr)
    
    return q_expr, q_expr, services_queryset, products_queryset

def check_distance(query_params: dict[str, Any], services_queryset: QuerySet, products_queryset: QuerySet):
    location = Point(query_params.get("distance"), srid=4326)
    
    services_q_expr = Q(provider_location__location__distance_lt=(location, 1000000))
    products_q_expr = Q(service_provider_location__location__distance_lt=(location, 1000000))
    
    services_queryset = services_queryset.annotate(
        distance=Distance("provider_location__location", location)).order_by("distance")
    products_queryset = products_queryset.annotate(
        distance=Distance("service_provider_location__location", location)).order_by("distance")
    
    return services_q_expr, products_q_expr, services_queryset, products_queryset

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
def search_in_services_products(request: Request):
    # first we get the language and query_params, then we make main querysets
    language, query_params = request.META.get("Accept-Language"), request.query_params
    services_main_queryset, products_main_queryset = Service.objects, Product.objects
    
    # then we get the callabels which mapped with the served query_params, and take care of pagination num
    callables, query_params, pagination_number = get_callables(query_params)
    
    # then we prepare the Q_exprs that will filter the querysets
    # we stand on callabels and query_params from the last step
    services_Q_exprs, products_Q_exprs = set(), set()
    for func in callables:
        services_Q_expr, products_Q_expr, services_main_queryset, products_main_queryset = func(
            query_params, services_main_queryset, products_main_queryset)
        services_Q_exprs.add(services_Q_expr)
        products_Q_exprs.add(products_Q_expr)
    
    # here we apply filtering (if exists) on the querysets
    services_main_queryset = services_main_queryset.filter(*services_Q_exprs)
    products_main_queryset = products_main_queryset.filter(*products_Q_exprs)
    
    # paginate the queryset under the client-side rules
    a, b = get_pagination(pagination_number)
    services_paginator = custom_pagination_function(a)
    paginated_services = services_paginator.paginate_queryset(services_main_queryset, request)
    products_paginator = custom_pagination_function(b)
    paginated_products = products_paginator.paginate_queryset(products_main_queryset, request)
    
    # serializing the queryset data
    serialized_services = RUDServicesSerializer(paginated_services, many=True, language=language)
    serialized_products = ProudctSerializer(paginated_products, many=True, language=language)
    
    return Response(data=serialized_services.data + serialized_products.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def overall_search_stats(req: Request):
    language = req.META.get("Accept-Language")
    # longitude, latitude = req.query_params.get("longitude"), req.query_params.get("latitude")
    # if not (longitude and latitude):
    #     return Response({"message": "longitude & latitude are needed"}, status=status.HTTP_400_BAD_REQUEST)
    
    main_services_queryset, main_products_queryset = Service.objects, Product.objects
    
    def find_prices(services_queryset: QuerySet, products_queryset: QuerySet):
        services = services_queryset.aggregate(max=Max("price"), min=Min("price"))
        products = products_queryset.aggregate(max=Max("price"), min=Min("price"))
        
        return min(services["min"], products["min"]), max(services["max"], products["max"])
    min_price, max_price = find_prices(main_services_queryset, main_products_queryset)
    
    def find_rates(services_queryset: QuerySet, products_queryset: QuerySet):
        limits = {(4.5, 5): 5, (3.5, 4.5): 4, (2.5, 3.5): 3, (1.5, 2.5): 2, (0.5, 1.5): 1, (0, 0.5): 0}
        rates = defaultdict(int)
        
        for queryset in [services_queryset.all(), products_queryset.all()]:
            for query in queryset:
                for limit in limits:
                    if query.average_rating >= limit[0] and query.average_rating < limit[1]:
                        rates[limits[limit]] += 1
                        break
        
        return rates
    rates = find_rates(main_services_queryset, main_products_queryset)
    
    def find_categories(services_queryset: QuerySet, products_queryset: QuerySet):
        categories = defaultdict(int)
        
        for product in products_queryset.all():
            product_repeat = product.service_provider_location.service_provider.category
            if language == "en":
                categories[product_repeat.en_name] += 1
            else:
                categories[product_repeat.ar_name] += 1
        
        for service in services_queryset.all():
            if language == "en":
                categories[service.category.en_name] += 1
            else:
                categories[service.category.ar_name] += 1
        
        return categories
    categories = find_categories(main_services_queryset, main_products_queryset)
    
    def find_location(sevices_queryset: QuerySet, products_queryset: QuerySet):
        pass
    locations = find_location(main_services_queryset, main_products_queryset)
    
    response_data = {
        "price": {"min_price": min_price, "max_price": max_price},
        "rates": rates,
        "categories": categories,
        "locations": locations
    }
    
    return Response(data=response_data, status=status.HTTP_200_OK)

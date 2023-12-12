from django.db.models import Q

from . import models

from functools import reduce



def searching_func(category_name, language: str):
    text_seq = category_name.split(" ")
    
    q_expression = (
        Q(service_provider_location__service_provider__category__en_name__icontains=x) for x in text_seq)
    if language == "ar":
        q_expression = (
            Q(service_provider_location__service_provider__category__ar_name__icontains=x) for x in text_seq)
    
    query_func = reduce(lambda x, y: x & y, q_expression)
    queryset = models.Product.objects.filter(query_func)
    return queryset

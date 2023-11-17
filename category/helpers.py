from django.http import HttpRequest
from django.db.models import Q

from functools import reduce

from users.models import UserIP
from . import models


def choose_lang(request):
    """
    this function checking two things:
    1] if there is a language header 
    2] and if there is a record with the same IP Address
    
    if not 1] and 2] => return language from DB
    if 1] and 2] => update language from DB, then return it
    if 1] and not 2] => create UserIP model record, then return language
    """
    
    IP_Address = request.META.get("REMOTE_ADDR")
    language_code = request.headers.get("Accept-Language")
    obj = UserIP.objects.filter(ip_address=IP_Address)
    
    if obj.exists():
        obj = obj.first()
        if language_code:
            obj.language_code = language_code
            obj.save()
    
    elif not obj.exists():
        obj = UserIP.objects.create(
            ip_address=IP_Address
            , language_code=language_code)
    
    return f"{obj.language_code}_name"


def searching_func(request: HttpRequest, third_field: str):
    search_key: str = request.query_params.get("query") # str | None
    text_seq = search_key.split(" ")
    if third_field == "ar_name":
        text_qs = reduce(lambda x, y: x & y
                    , (Q(ar_name__icontains=x) for x in text_seq) )
    else:
        text_qs = reduce(lambda x, y: x & y
                    , (Q(en_name__icontains=x) for x in text_seq) )
    
    queryset = models.Category.objects.filter(text_qs)
    return queryset

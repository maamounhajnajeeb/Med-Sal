from rest_framework import decorators, status
from rest_framework.response import Response

from django.http import HttpRequest


@decorators.api_view(["POST", ])
def change_language(request: HttpRequest):
    ip_address = request.headers.get("IP_Address")
    lang_code = request.LANGUAGE_CODE
    
    return Response({
        "message": "language_changed"
        , "ip_address": ip_address
        , "lang_code": lang_code}
        , status=status.HTTP_200_OK)

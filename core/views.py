from rest_framework import decorators, status
from rest_framework.response import Response

from django.http import HttpRequest



@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def language_switcher(request: HttpRequest):
    return Response({"message": "language switched successfully"}, status=status.HTTP_200_OK)

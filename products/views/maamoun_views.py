from rest_framework import generics, decorators
from rest_framework.response import Response
from rest_framework import permissions

from django.http import HttpRequest

from products import models, serializers



class CreateProduct(generics.CreateAPIView):
    queryset = models.Product
    serializer_class = serializers.ProudctSerializer
    permission_classes = (permissions.AllowAny, )
    
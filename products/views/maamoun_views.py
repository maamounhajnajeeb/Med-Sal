from rest_framework import decorators, generics
from rest_framework import permissions, status
from rest_framework.response import Response

from django.http import HttpRequest

from products import permissions as local_permissions
from products import models, serializers
from products import file_handler



class AllProducts(generics.ListAPIView):
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product


class CreateProduct(generics.CreateAPIView):
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product


class RUDProduct(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_category(request: HttpRequest, pk: int):
    """
    get all products for specific category
    pk here is category_id
    for everybody
    """
    queryset = models.Product.objects.filter(service_provider_location__service_provider__category=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_location(request: HttpRequest, pk: int):
    """
    get all products for specific location
    pk here is location_id
    for everybody
    """
    queryset = models.Product.objects.filter(service_provider_location=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_provider(request: HttpRequest, pk: int):
    """
    get all products for specific service provider
    pk here is service_provider_id
    for everybody
    """
    queryset = models.Product.objects.filter(service_provider_location__service_provider=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

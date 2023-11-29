from rest_framework import permissions, decorators
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpRequest

from orders import models, serializers



class CreateOrder(generics.CreateAPIView):
    """
    create an order cart for patients
    patient can put one product or more with each order cart
    it takes patient_id and chosen product/s with quantity as array of json/s
    if no quantity added, 1 is the default quantity
    status, updated_at, created_at added implicity
    is_authenticated permission implicity added
    """
    serializer_class = serializers.OrdersSerializer
    queryset = models.Orders.objects
    
    def create(self, request: HttpRequest, *args, **kwargs):
        data = request.data.copy()
        data["patient"] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ListAllOrders(generics.ListAPIView):
    """
    give admins the ability to see all orders for all service prodviders
    """
    permission_classes = ()
    serializer_class = serializers.ListOrderSer
    queryset = models.Orders.objects
    
    def list(self, request: HttpRequest, *args, **kwargs):
        language = request.META.get("Accept-Language")
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.serializer_class(queryset, many=True, fields={"language": language})
        return Response(serializer.data, status=status.HTTP_200_OK)


class LocationOrders(generics.ListAPIView):
    """
    give service providers and admins ability to see overall orders in specific location
    (pended, rejected, accepted) orders
    take id as parameter (which is location id)
    """
    serializer_class = serializers.LocationOrdersSer
    queryset = models.OrderItem.objects
    permission_classes = ()
    
    def get_queryset(self):
        return self.queryset.filter(product__service_provider_location=self.kwargs.get("pk"))
    
    def list(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.serializer_class(queryset, many=True, fields={"language": language})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceProviderOrders(generics.ListAPIView):
    """
    give service providers and admins ability to see overall orders for specific service provider
    (pended, rejected, accepted) orders
    take id as parameter (which is service_provider id)
    """
    serializer_class = serializers.LocationOrdersSer
    queryset = models.OrderItem.objects
    permission_classes = ()
    
    def get_queryset(self):
        return self.queryset.filter(product__service_provider_location__service_provider=self.kwargs.get("pk"))
    
    def list(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.serializer_class(queryset, many=True, fields={"language": language})
        return Response(serializer.data, status=status.HTTP_200_OK)


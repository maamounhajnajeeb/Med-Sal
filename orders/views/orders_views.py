from rest_framework import decorators, status
from rest_framework import viewsets, generics
from rest_framework.response import Response

from django.http import HttpRequest

from typing import Optional

from orders import permissions as local_permissions
from orders import models, serializers

from utils.permission import authorization



class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Orders.objects
    permission_classes = (local_permissions.HasPermission, )
    serializer_class = serializers.OrdersSerializer
    
    def get_permissions(self):
        return [permission("orders") for permission in self.permission_classes]
    
    def create(self, request: HttpRequest, *args, **kwargs):
        """
        we add the patient id to the data, so we don't need it from the front-end
        """
        data = request.data.copy()
        data["patient"] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def list(self, request, *args, **kwargs):
        """
        return all orders for all users
        """
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """
        return specific order by order_id
        """
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        update order status and pay status
        """
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance: models.Orders = self.get_object()
        if instance.status == "PENDING":
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(
            {"message": "You can't delete this order, already accepted"}
            , status=status.HTTP_204_NO_CONTENT)


@decorators.api_view(["GET", ])
@decorators.permission_classes([local_permissions.HasPermission, ])
def user_orders(request: HttpRequest, user_id: Optional[int]):
    """
    user orders with it's items (you can put the user id, or via authenticated id)
    """
    user_id = user_id or request.user.id
    queryset = models.Orders.objects.filter(patient=user_id)
    serializer = serializers.OrdersSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


class ReadUpdateDestroyItem(generics.RetrieveUpdateDestroyAPIView):
    """
    give the user the ability to change or delete an element from the order if it is still pending
    there is a retrieve function too.
    """
    queryset = models.OrderItem.objects
    permission_classes = (local_permissions.HasPermission, )
    serializer_class = serializers.ItemsSerializer
    
    def get_permissions(self):
        return [permission("orders") for permission in self.permission_classes]
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        just for cahanging item status
        if rejected it goes to rejected
        if accepted we edit related product quantity 
        """
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return Response(
            {"message": f"You can't {request.method} the item after it is submitted"}
            , status=status.HTTP_403_FORBIDDEN
            )


@decorators.api_view(["GET", ])
@authorization("orderitem")
def user_items(request: HttpRequest, pk: Optional[int]):
    """
    user submited order items
    """
    user_id = pk or request.user.id
    queryset = models.OrderItem.objects.filter(order__patient=user_id)
    serializer = serializers.ItemsSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([local_permissions.ListItemsPermission, ])
def all_items(request: HttpRequest):
    queryset = models.OrderItem.objects.all()
    serializer = serializers.ItemsSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([local_permissions.ListItemsPermission, ])
def filter_items(request: HttpRequest, stat: str):
    """
    take {PENDING, ACCEPTED or REJECTED} as a parameter
    and filtering depending on this parameter
    for admins only
    """
    queryset = models.OrderItem.objects.filter(status=stat)
    serializer = serializers.ItemsSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@authorization("orderitem")
def provider_items(request: HttpRequest, provider_id: Optional[int]):
    """
    return service provider ordered items
    provider_id parameter is optional
    if there is no provider_id, it take it from the request
    """
    provider_id = provider_id or request.user.id
    queryset = models.OrderItem.objects.filter(
        product__service_provider_location__service_provider=provider_id)
        
    serializer = serializers.ItemsSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@authorization("orderitem")
def location_items(request: HttpRequest, location_id: int):
    """
    return service provider location ordered items
    location_id parameter is optional
    if there is no location_id, it take it from the request
    """
    queryset = models.OrderItem.filter(order__product__service_provider_location=location_id)
    serializer = serializers.ItemsSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

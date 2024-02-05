from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework import decorators

from typing import Optional

from orders import models, serializers

from utils.permission import HasPermission



class RejectedOrdersViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RejectedOrderSerializer
    queryset = models.RejectedOrders.objects
    permission_classes = (HasPermission, )
    
    def get_permissions(self):
        return [permission("rejectedorders") for permission in self.permission_classes]


@decorators.api_view(["GET", ])
def user_rejected_orders(request: Request, user_id: Optional[int]):
    user_id = user_id or request.user.id
    queryset = models.RejectedOrders.objects.filter(order__order__patient=user_id)
    serializer = serializers.RejectedOrderSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def provider_rejected_orders(request: Request, provider_id: Optional[int]):
    provider_id = provider_id or request.user.id
    queryset = models.RejectedOrders.objects.filter(
        order__product__service_provider_location__service_provider=provider_id)
    serializer = serializers.RejectedOrderSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def location_rejected_orders(request: Request, location_id: int):
    queryset = models.RejectedOrders.objects.filter(
        order__product__service_provider_location=location_id)
    serializer = serializers.RejectedOrderSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

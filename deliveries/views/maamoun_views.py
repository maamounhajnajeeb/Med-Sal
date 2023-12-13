from rest_framework import viewsets, decorators
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpRequest

from typing import Optional

from deliveries import models, serializers

from utils.permission import HasPermission, authorization, authorization_with_method



class DeliveryViewSet(viewsets.ModelViewSet):
    permission_classes = (HasPermission, )
    queryset = models.Delivery.objects
    serializer_class = serializers.DeliverySerializer
    
    def get_permissions(self):
        return [permission("delivery") for permission in self.permission_classes]
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        fields = {"language": request.META.get("Accept-Language")}
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, fields=fields)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        fields = {"language": request.META.get("Accept-Language")}
        instance = self.get_object()
        serializer = self.get_serializer([instance, ], many=True, fields=fields)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        fields = {"language": request.META.get("Accept-Language")}
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, fields=fields)
        return Response(serializer.data)


@decorators.api_view(["GET", ])
@authorization("delivery")
def provider_deliveries(request: HttpRequest, provider_id: Optional[int]):
    fields = {"language": request.META.get("Accept-Language")}
    provider_id = provider_id or request.user.id
    
    queryset = models.Delivery.objects.filter(
        order__product__service_provider_location__service_provider=provider_id)
    serializer = serializers.DeliverySerializer(queryset, many=True, fields=fields)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@authorization("delivery")
def user_deliveries(request: HttpRequest, user_id: Optional[int]):
    fields = {"language": request.META.get("Accept-Language")}
    user_id = user_id or request.user.id
    
    queryset = models.Delivery.objects.filter(order__order__patient=user_id)
    serializer = serializers.DeliverySerializer(queryset, many=True, fields=fields)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework import generics, decorators
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from django.http import HttpRequest

from typing import Optional

from orders import serializers, models

from notification.models import Notification
from utils.permission import authorization, authorization_with_method, HasPermission



@decorators.api_view(["GET", ])
@authorization_with_method("list", "orders")
def list_all_orders(request: HttpRequest):
    language = request.META.get("Accept-Language")
    queryset = models.Orders.objects.all()
    
    serializer = serializers.OrdersSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


class CreateOrder(generics.CreateAPIView):
    serializer_class = serializers.OrdersSerializer
    queryset = models.Orders.objects
    permission_classes = (HasPermission, )
    
    def get_permissions(self):
        return [permission("orders") for permission in self.permission_classes]
    
    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault("language", self.request.META.get("Accept-Language"))
        return super().get_serializer(*args, **kwargs)
    
    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        data["patient"] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.id, receiver_type="User"
            , ar_content="تم تأكيد العملية"
            , en_content="Operation confirmed")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RetrieveDestroyOrders(generics.RetrieveDestroyAPIView):
    queryset = models.Orders.objects
    serializer_class = serializers.OrdersSerializer
    permission_classes = (HasPermission, )
    
    def get_permissions(self):
        return [permission("orders") for permission in self.permission_classes]
    
    def retrieve(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        
        instance = self.get_object()
        serializer = self.get_serializer([instance, ], many=True, language=language)
        return Response(serializer.data)


@decorators.api_view(["GET", ])
@authorization("orders")
def user_orders(request: HttpRequest, user_id: Optional[int]):
    language = request.META.get("Accept-Language")
    
    user_id = user_id or request.user.id
    queryset = models.Orders.objects.filter(patient=user_id)
    
    serializer = serializers.OrdersSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

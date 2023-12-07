from rest_framework import generics, decorators
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpRequest

from typing import Optional

from orders import models, serializers

from utils.permission import HasPermission, authorization_with_method
from notification.models import Notification



class RetrieveDestroyUpdateItem(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (HasPermission, )
    queryset = models.OrderItem.objects
    serializer_class = serializers.SpecificItemSerialzier
    
    def get_permissions(self):
        return [permission("orderitem") for permission in self.permission_classes]
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", language)
        
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.queryset.filter(id=self.kwargs.get("pk"))
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        if the update have accepted, record automatically goes to Delivery table
        else if the update have rejected, you need to create rejected order by your hand
        """
        resp = super().update(request, *args, **kwargs)
        
        Notification.objects.create(
            sender=f"{request.user.email}"
            , sender_type="Service_Provider"
            , receiver=f"{resp.data.get('user_email')}"
            , receiver_type="User"
            , en_content=f"your order {resp.data.get('status')}"
            , ar_content="تم رفض طلبك" if resp.data.get('status') == "REJECTED" else "تم قبول طلبك")
        
        return Response(resp.data, status=resp.status_code)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@decorators.api_view(["GET", ])
@authorization_with_method("list", "orderitems")
def list_all_items(request: HttpRequest):
    language = request.META.get("Accept-Language")
    
    queryset = models.OrderItem.objects.all()
    serializer = serializers.SpecificItemSerialzier(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def user_items(request: HttpRequest, user_id: Optional[int]):
    language = request.META.get("Accept-Language")
    user_id = user_id or request.user.id
    
    queryset = models.OrderItem.objects.filter(order__patient=user_id)
    serializer = serializers.SpecificItemSerialzier(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def provider_items(request: HttpRequest):
    language = request.META.get("Accept-Language")
    
    query_params = request.query_params.copy()
    try:
        provider_id = (query_params.pop("provider_id")[0])
    except:
        provider_id = request.user.id
    
    additional_fields = {f"last_update__{param}": value for param, value in query_params.items()}
    queryset = models.OrderItem.objects.filter(
        product__service_provider_location__service_provider=provider_id, **additional_fields)
    
    serializer = serializers.SpecificItemSerialzier(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

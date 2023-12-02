from rest_framework import viewsets, decorators
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpRequest

from typing import Optional

from products import models, serializers



class RatesViewSet(viewsets.ModelViewSet):
    queryset = models.ProductRates.objects
    serializer_class = serializers.RateSerializer
    
    def create(self, request: HttpRequest, *args, **kwargs):
        data = request.data
        data["user"] = request.user.id
        
        serializer = self.get_serializer(data=data, fields={"language": request.META.get("Accept-Language")})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance], many=True, fields={"language": request.META.get("Accept-Language")})
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, fields={"language": language})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@decorators.api_view(["GET", ])
def user_rates(request: HttpRequest, user_id: Optional[int]):
    language = request.META.get("Accept-Language")
    user_id = user_id or request.user.id
    
    queryset = models.ProductRates.objects.filter(user=user_id)
    serializer = serializers.RateSerializer(queryset, many=True, fields={"language": language})
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def provider_rates(request: HttpRequest, provider_id: Optional[int]):
    language = request.META.get("Accept-Language")
    provider_id = provider_id or request.user.id
    
    queryset = models.ProductRates.objects.filter(
        product__service_provider_location__service_provider=provider_id)
    serializer = serializers.RateSerializer(queryset, many=True, fields={"language": language})
    
    return Response(serializer.data, status=status.HTTP_200_OK)

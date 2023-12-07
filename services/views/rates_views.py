from rest_framework import viewsets, decorators
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpRequest

from typing import Optional

from services import models, serializers
from utils.permission import HasPermissionAndOwner



class ServiceRatesViewSet(viewsets.ModelViewSet):
    permission_classes = (HasPermissionAndOwner, )
    serializer_class = serializers.ServiceRatesSerializer
    queryset = models.ServiceRates.objects
    
    def get_permissions(self):
        return [permission("servicerates") for permission in self.permission_classes]
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs["language"] = language
        
        return super().get_serializer(*args, **kwargs)
    
    def create(self, request: HttpRequest, *args, **kwargs):
        request.data["user"] = request.user.id
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
        except:
            return Response({"error": "this user already rate this service, user can't rate same service twice"})
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance, ], many=True)
        return Response(serializer.data)


@decorators.api_view(["GET", ])
def location_rates(request: HttpRequest, location_id: int):
    language = request.META.get("Accept-Language")
    queryset = models.ServiceRates.objects.filter(service__provider_location=location_id)
    serializer = serializers.ServiceRatesSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def provider_rates(request: HttpRequest, provider_id: Optional[int]):
    provider_id = provider_id or request.user.id
    language = request.META.get("Accept-Language")
    queryset = models.ServiceRates.objects.filter(
        service__provider_location__service_provider=provider_id)
    serializer = serializers.ServiceRatesSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def user_rates(request: HttpRequest, user_id: Optional[int]):
    user_id = user_id or request.user.id
    language = request.META.get("Accept-Language")
    queryset = models.ServiceRates.objects.filter(user__id=user_id)
    serializer = serializers.ServiceRatesSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

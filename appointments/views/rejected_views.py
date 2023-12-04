from rest_framework import status, decorators
from rest_framework.response import Response
from rest_framework import generics

from django.http import HttpRequest

from typing import Optional

from appointments import models, serializers



class AllRejectedAppointments(generics.ListAPIView):
    queryset = models.RejectedAppointments.objects
    serializer_class = serializers.RejectedSerializer
    # permission_classes = ("for admins only")
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", language)
        
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)


class CreateRejectedAppointment(generics.CreateAPIView):
    queryset = models.RejectedAppointments.objects
    serializer_class = serializers.RejectedSerializer
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", language)
        
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)


class RUDRejectedAppointments(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.RejectedAppointments.objects
    serializer_class = serializers.RejectedSerializer
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", language)
        
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)
    
    def retrieve(self, request: HttpRequest, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance,], many=True)
        return Response(serializer.data)


@decorators.api_view(["GET",])
def user_rejected_appointments(request: HttpRequest, user_id: Optional[int]):
    language = request.META.get("Accept-Language")
    user_id = user_id or request.user.id
    queryset = models.RejectedAppointments.objects.filter(appointment__user=user_id)
    serializer = serializers.RejectedSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def provider_rejected_appointments(request: HttpRequest, provider_id: Optional[int]):
    language = request.META.get("Accept-Language")
    provider_id = provider_id or request.user.id
    queryset = models.RejectedAppointments.objects.filter(
        appointment__service__provider_location__service_provider=provider_id)
    serializer = serializers.RejectedSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def location_rejected_appointments(request: HttpRequest, location_id: int):
    language = request.META.get("Accept-Language")
    location_id = location_id or request.user.id
    queryset = models.RejectedAppointments.objects.filter(
        appointment__service__provider_location=location_id)
    serializer = serializers.RejectedSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

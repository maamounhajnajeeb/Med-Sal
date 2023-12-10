from rest_framework import status, decorators
from rest_framework.response import Response
from rest_framework import generics

from django.http import HttpRequest

from typing import Optional

from appointments import models, serializers
from notification.models import Notification



class CreateAppointment(generics.CreateAPIView):
    queryset = models.Appointments.objects
    serializer_class = serializers.AppointmentSerializer
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", language)
        return super().get_serializer(*args, **kwargs)
    
    def create(self, request: HttpRequest, *args, **kwargs):
        data = request.data.copy()
        data["user"] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        Notification.objects.create(
            sender=request.user.email, sender_type="User"
            , receiver=instance.service.provider_location.service_provider.email
            , receiver_type="Service_Provider"
            , ar_content="موعدك على قائمة المراجعة لدى مزود الخدمة"
            , en_content="Your appointments is waiting to be checked from service provider")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer) -> models.Appointments:
        return serializer.save()


class AppointmentRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Appointments.objects
    serializer_class = serializers.AppointmentSerializer
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", language)
        return super().get_serializer(*args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance, ], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance: models.Appointments = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        if request.data.get("status"):
            ar_word = "مقبول" if request.data.get("status") == "accepted" else "مرفوض"
            Notification.objects.create(
                sender_type="Service_Provider", sender=request.user.email, receiver_type="User"
                , receiver=instance.user
                , ar_content=f"موعدك {ar_word} مع {instance.service.provider_location.service_provider.business_name}"
                , en_content=f"Your Appointment has been {request.data.get('status')}")
        
        return Response(serializer.data)


@decorators.api_view(["GET", ])
def all_location_appointments(request: HttpRequest, location_id: int):
    """
    get all appointments for specific provider location
    """
    language = request.META.get("Accept-Language")
    queryset = models.Appointments.objects.filter(service__provider_location=location_id)
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def all_provider_appointments(request: HttpRequest, provider_id: Optional[int]):
    """
    get all appointments for specific provider
    """
    language = request.META.get("Accept-Language")
    provider_id = provider_id or request.user.id
    queryset = models.Appointments.objects.filter(
        service__provider_location__service_provider=provider_id)
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def all_user_appointments(request: HttpRequest, user_id: Optional[int]):
    """
    get all user appointments 
    """
    language = request.META.get("Accept-Language")
    user_id = user_id or request.user.id
    
    queryset = models.Appointments.objects.filter(user__id=user_id)
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

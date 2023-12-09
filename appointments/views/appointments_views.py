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
        # language = request.META.get("Accept-Language")
        # data = request.data.copy()
        request.data["user"] = request.user.id
        resp = super().create(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="User"
            , ar_content="موعدك على قائمة المراجعة لدى مزود الخدمة"
            , en_content="Your appointments is waiting to be checked from service provider")
        
        return Response(resp.data, status=status.HTTP_200_OK)
    
    # def get_serializer(self, *args, **kwargs):
        
    #     serializer_class = self.get_serializer_class()
    #     kwargs.setdefault('context', self.get_serializer_context())
    #     return serializer_class(*args, **kwargs)
    
    # def create(self, request: HttpRequest, *args, **kwargs):
        
    #     serializer = self.get_serializer(data=data, language=language)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AppointmentRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Appointments.objects
    serializer_class = serializers.AppointmentSerializer
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", language)
        
        return super().get_serializer(*args, **kwargs)
        
        # serializer_class = self.get_serializer_class()
        # kwargs.setdefault('context', self.get_serializer_context())
        # return serializer_class(*args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance, ], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        if request.data.get("status"):
            ar_word = "مقبول" if request.data.get("status") == "accepted" else "مرفوض"
            Notification.objects.create(
                sender_type="Service_Provider", sender=request.user.email, receiver_type="User"
                , reveiver=models.Appointments.objects.get(id=self.kwargs.get("id")).user.email
                , ar_content=f"موعدك {ar_word}"
                , en_content=f"Your Appointment has been {request.data.get('status')}")
        
        return super().update(request, *args, **kwargs)


@decorators.api_view(["GET", ])
def accepted_location_appointments(request: HttpRequest, location_id: int):
    """
    get all accepted appointments for specific provider location
    """
    language = request.META.get("Accept-Language")
    queryset = models.Appointments.objects.filter(service__provider_location=location_id, status="accepted")
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def accepted_provider_appointments(request: HttpRequest, provider_id: Optional[int]):
    """
    get all accepted appointments for specific provider
    """
    language = request.META.get("Accept-Language")
    provider_id = provider_id or request.user.id
    queryset = models.Appointments.objects.filter(
        service__provider_location__service_provider=provider_id, status="accepted")
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


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
    user_id = user_id or request.user.id
    queryset = models.Appointments.objects.filter(
        service__provider_location__service_provider=provider_id)
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def accepted_user_appointments(request: HttpRequest, user_id: Optional[int]):
    """
    get all user accepted appointments
    """
    language = request.META.get("Accept-Language")
    user_id = user_id or request.user.id
    
    queryset = models.Appointments.objects.filter(user__id=user_id, status="accepted")
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

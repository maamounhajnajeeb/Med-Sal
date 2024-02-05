from rest_framework import status, decorators
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import generics

from django.db.models import Count, Q

from datetime import datetime
from typing import Optional

from utils.permission import authorization_with_method, HasPermission
from appointments import models, serializers
from notification.models import Notification



class CreateAppointment(generics.CreateAPIView):
    queryset = models.Appointments.objects
    serializer_class = serializers.AppointmentSerializer
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", language)
        return super().get_serializer(*args, **kwargs)
    
    def create(self, request: Request, *args, **kwargs):
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
    permission_classes = (HasPermission, )
    queryset = models.Appointments.objects
    serializer_class = serializers.AppointmentSerializer
    
    def get_permissions(self):
        return [permission("appointments") for permission in self.permission_classes]
    
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
            business_name = instance.service.provider_location.service_provider.business_name
            Notification.objects.create(
                receiver_type="User", receiver=instance.user
                , sender_type="Service_Provider", sender=business_name
                , ar_content=f"موعدك {ar_word} مع {business_name}"
                , en_content=f"Your Appointment has been {request.data.get('status')}")
        
        return Response(serializer.data)


@decorators.api_view(["GET", ])
@authorization_with_method("list", "appointments")
def provider_today_appointments(req: Request):
    language = req.META.get("Accept-Language")
    provider_id = req.user.id
    
    main_queryset = models.Appointments.objects.filter(
        service__provider_location__service_provider=provider_id)
    
    last_five_queryset = main_queryset.filter(result__isnull=False).order_by("-updated_at")[5:]
    
    date = datetime.now()
    day, month, year = date.day, date.month, date.year
    today_appointments = main_queryset.filter(
        updated_at__day=day, updated_at__month=month, updated_at__year=year)
    
    last_five_serializer = serializers.DailyAppointmentsSerializer(
        last_five_queryset, many=True, language=language)
    today_serializer = serializers.DailyAppointmentsSerializer(
        today_appointments, many=True, language=language)
    
    response = {
        "last_five": last_five_serializer.data,
        "today_appointments": today_serializer.data
    }
    
    return Response(data=response, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@authorization_with_method("list", "appointments")
def location_today_appointments(req: Request):
    language = req.META.get("Accept-Language")
    location_id = req.query_params.get("provider_id")
    if not location_id:
        return Response({
            "message": "Sorry, but location_id needed for using this API"}, status=status.HTTP_200_OK)
    
    location_id = int(location_id)
    main_queryset = models.Appointments.objects.filter(service__provider_location=location_id)
    
    last_five_queryset = main_queryset.filter(result__isnull=False).order_by("-updated_at")[5:]
    
    date = datetime.now()
    day, month, year = date.day, date.month, date.year
    today_appointments = main_queryset.filter(
        updated_at__day=day, updated_at__month=month, updated_at__year=year)
    
    last_five_serializer = serializers.DailyAppointmentsSerializer(
        queryset=last_five_queryset, many=True, language=language)
    today_serializer = serializers.DailyAppointmentsSerializer(
        queryset=today_appointments, many=True, language=language)
    
    return Response(last_five_serializer+today_serializer, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@authorization_with_method("view", "appointments")
def all_location_appointments(request: Request, location_id: int):
    """
    get all appointments for specific provider location
    """
    language = request.META.get("Accept-Language")
    queryset = models.Appointments.objects.filter(service__provider_location=location_id)
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@authorization_with_method("list", "appointments")
def all_provider_appointments(request: Request, provider_id: Optional[int]):
    """
    get all appointments for specific provider
    """
    language = request.META.get("Accept-Language")
    provider_id = provider_id or request.user.id
    queryset = models.Appointments.objects.filter(service__provider_location__service_provider=provider_id)
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def all_user_appointments(request: Request, user_id: Optional[int]):
    """
    get all user appointments 
    """
    language = request.META.get("Accept-Language")
    user_id = user_id or request.user.id
    
    queryset = models.Appointments.objects.filter(user__id=user_id)
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@authorization_with_method("view", "appointments")
def provider_appointments_dashborad(req: Request):
    # this trick because maybe admin want to see or provider
    language = req.META.get("Accept-Language")
    provider_id = req.query_params.get("provider_id")
    if provider_id:
        provider_id = int(provider_id)
    else:
        provider_id = req.user.id
    
    queryset = models.Appointments.objects.filter(
        service__provider_location__service_provider=provider_id)
    
    stats = queryset.aggregate(
        all=Count("id"), rejected=Count("id", filter=Q(status="rejected")),
        accepted=Count("id", filter=Q(status="accepted")),
        pended=Count("id", filter=Q(status="pending")))
    
    if req.query_params.get("appointment_stauts"):
        appointment_status = req.query_params.get("appointment_status")
        if appointment_status not in ["pending", "accepted", "rejected"]:
            return Response(
                {"message": "appointment_status should be one of those: ['pending','accepted','rejected']"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        appointment_filter = appointment_status
        queryset = queryset.filter(status=appointment_filter)
    
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    
    response_data = {
        "stats": {
            "all": stats["all"], "rejected": stats["rejected"],
            "accepted": stats["accepted"], "pended": stats["pended"]
            },
        "appointments": serializer.data
    }
    return Response(data=response_data, status=status.HTTP_200_OK)

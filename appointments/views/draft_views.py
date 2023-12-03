from rest_framework import status, decorators
from rest_framework.response import Response
from rest_framework import generics

from django.http import HttpRequest

from appointments import models, serializers

from notification.models import Notification

from utils.permission import authorization_with_method



class CreateDraft(generics.CreateAPIView):
    serializer_class = serializers.DraftSerializers
    queryset = models.AppointmentsDraft.objects
    
    def create(self, request: HttpRequest, *args, **kwargs):
        data = request.data.copy()
        data["user"] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        Notification.objects.create(
            sender=request.user.email, sender_type="User"
            , receiver=serializer.data.get("provider"), receiver_type="Service_Provider"
            , ar_content="طلب موعد جديد بانتظار المراجعة"
            , en_content="A new appointment draft added to box")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RUDDraft(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.DraftSerializers
    queryset = models.AppointmentsDraft.objects
    
    def retrieve(self, request: HttpRequest, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance, ], many=True)
        return Response(serializer.data)


@decorators.api_view(["GET", ])
def provider_drafts(request: HttpRequest):
    language = request.META.get("Accept-Language")
    queryset = models.AppointmentsDraft.objects.filter(
        service__provider_location__service_provider=request.user.id)
    
    serializer = serializers.DraftSerializers(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def user_drafts(request: HttpRequest):
    language = request.META.get("Accept-Language")
    queryset = models.AppointmentsDraft.objects.filter(user=request.user.id)
    
    serializer = serializers.DraftSerializers(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@authorization_with_method("list", "drafts")
def all_drafts(request: HttpRequest):
    language = request.META.get("Accept-Language")
    
    queryset = models.AppointmentsDraft.objects.all()
    serializer = serializers.DraftSerializers(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

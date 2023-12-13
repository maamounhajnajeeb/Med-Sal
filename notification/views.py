from rest_framework import generics, decorators
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpRequest

from . import models, serializers

from utils.permission import HasPermission, authorization, authorization_with_method



class RUDNotification(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Notification.objects
    serializer_class = serializers.NotificationSerializer
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs["language"] = language
        
        return super().get_serializer(*args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance, ], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@decorators.api_view(["GET", ])
def provider_notifications(request: HttpRequest):
    language = request.META.get("Accept-Language")
    
    queryset = models.Notification.objects.filter(
        receiver_type="Service_Provider", receiver=request.user.email)
    serializer = serializers.NotificationSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def user_notifications(request: HttpRequest):
    language = request.META.get("Accept-Language")
    
    queryset = models.Notification.objects.filter(
        receiver_type="User", receiver=request.user.email)
    serializer = serializers.NotificationSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def admin_notifications(request: HttpRequest):
    language = request.META.get("Accept-Language")
    
    queryset = models.Notification.objects.filter(
        receiver_type="Admin", receiver=request.user.email)
    serializer = serializers.NotificationSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

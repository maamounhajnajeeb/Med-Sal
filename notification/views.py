from rest_framework import generics, decorators
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpRequest

from . import models, serializers

from utils.permission import HasPermission, authorization, authorization_with_method



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

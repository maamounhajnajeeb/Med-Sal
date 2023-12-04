from rest_framework import generics, decorators
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpRequest

from services import models, serializers, helpers
from notification.models import Notification

from utils.permission import HasPermission, authorization



class CreateService(generics.CreateAPIView, helpers.FileMixin):
    serializer_class = serializers.CreateServicesSerializer
    permission_classes = (HasPermission, )
    queryset = models.Service.objects
    
    def get_permissions(self):
        return [permission("service") for permission in self.permission_classes]
    
    def create(self, request: HttpRequest, *args, **kwargs):
        image_objs = request.FILES.getlist("image")
        images_names = self.upload(image_objs, "service", request)
        
        data = request.data
        data["image"] = images_names
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        Notification.objects.create(
            sender="system", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , ar_content="تم إضافة خدمة جديدة إلى خدماتك"
            , en_content="A new service added to your sevices")
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ServiceRUD(generics.RetrieveUpdateDestroyAPIView, helpers.FileMixin):
    serializer_class = serializers.RUDServicesSerializer
    permission_classes = (HasPermission, )
    queryset = models.Service.objects
    
    def get_permissions(self):
        return [permission("service") for permission in self.permission_classes]
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs["language"] = language
        
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance, ], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        self.delete_images(instance.image)
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request: HttpRequest, *args, **kwargs):
        data = request.data
        
        if request.data.get("image"):
            images_objs = request.FILES.getlist("image")
            images_names = self.upload(images_objs, "service", request)
            data["image"] = images_names
            
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ListAllServices(generics.ListAPIView):
    serializer_class = serializers.RUDServicesSerializer
    queryset = models.Service.objects
    
from rest_framework import generics, decorators
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpRequest

from collections import defaultdict

from services import models, serializers, helpers

from products.file_handler import UploadImages, DeleteFiles
from notification.models import Notification
from utils.permission import HasPermission



class CreateService(generics.CreateAPIView, helpers.FileMixin):
    serializer_class = serializers.CreateServicesSerializer
    permission_classes = (HasPermission, )
    queryset = models.Service.objects
    
    def get_permissions(self):
        return [permission("service") for permission in self.permission_classes]
    
    def create(self, request: HttpRequest, *args, **kwargs):
        image_objs = request.FILES.getlist("image")
        upload_images = UploadImages(request)
        images_names = upload_images.upload_files("services", image_objs)
        
        request.data["image"] = images_names
        resp = super().create(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="system", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , ar_content="تم إضافة خدمة جديدة إلى خدماتك"
            , en_content="A new service added to your sevices")
        
        return Response(resp.data, status=resp.status_code)


class ServiceRUD(generics.RetrieveUpdateDestroyAPIView, helpers.FileMixin):
    serializer_class = serializers.RUDServicesSerializer
    permission_classes = (HasPermission, )
    queryset = models.Service.objects
    
    def get_permissions(self):
        return [permission("service") for permission in self.permission_classes]
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs["language"] = language
        return super().get_serializer(*args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance, ], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def perform_destroy(self, instance):
        delete_files = DeleteFiles()
        delete_files.delete_files(instance.image)
        
        Notification.objects.create(
            sender="system", sender_type="System"
            , receiver=self.request.user.email, receiver_type="Service_Provider"
            , ar_content="تم حذف الخدمة"
            , en_content="service has been deleted")
        
        return super().perform_destroy(instance)
    
    def update(self, request: HttpRequest, *args, **kwargs):
        data = request.data
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        if request.data.get("image"):
            image_objs = request.FILES.getlist("image")
            upload_images = UploadImages(request)
            images_names = upload_images.upload_files("services", image_objs)
            
            request.data["image"] = images_names
            
            delete_files = DeleteFiles()
            delete_files.delete_files(instance.image)
            
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        Notification.objects.create(
            sender="system", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , ar_content="تم تعديل الخدمة"
            , en_content="service has been updated")
        
        return Response(serializer.data)

#
class ListAllServices(generics.ListAPIView):
    serializer_class = serializers.RUDServicesSerializer
    queryset = models.Service.objects
    permission_classes = ( )
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs["language"] = language
        return super().get_serializer(*args, **kwargs)

#
@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def provider_services(request: HttpRequest, provider_id: int):
    provider_id = provider_id or request.user.id
    language = request.META.get("Accept-Language")
    queryset = models.Service.objects.filter(provider_location__service_provider=provider_id)
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

# 
@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def provider_services_by_category(request: HttpRequest, provider_id: int):
    language = request.META.get("Accept-Language")
    queryset = models.Service.objects.filter(provider_location__service_provider=provider_id)
    
    def aggregate_queryset(queryset):
        frequencies = defaultdict(int)
        for query in queryset:
            category_id = query.category.id
            category_name = query.category.en_name if language == "en" else query.category.ar_name 
            
            frequencies[(category_id, category_name)] += 1
        return frequencies
    
    def serialize_data(frequencies: defaultdict[tuple[int, str], int]):
        data = []
        for k, v in frequencies.items():
            data.append({"category_id": k[0], "category_name": k[1], "services_count": v})
        
        return data
    
    frequencies = aggregate_queryset(queryset)
    data = serialize_data(frequencies)
    
    return Response(data, status=status.HTTP_200_OK)

#
@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def provider_category_services(request: HttpRequest, provider_id: int, category_id: int):
    language = request.META.get("Accept-Language")
    queryset = models.Service.objects.filter(
        provider_location__service_provider=provider_id, category=category_id)
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

#
@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def category_services_by_name(request: HttpRequest, category_name: str):
    language = request.META.get("Accept-Language")
    queryset = helpers.searching_func(category_name)
    
    if not queryset.exists():
        return Response({"message": "No services found relates to this category"}
                    , status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def service_price_range(request: HttpRequest):
    language = request.META.get("Accept-Language")
    min_price, max_price = int(request.query_params["min_price"]), int(request.query_params["max_price"])
    
    queryset = models.Service.objects.filter(price__range=(min_price, max_price))
    if not queryset.exists():
        return Response({
            "message": "No services found within this range"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

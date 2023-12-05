from rest_framework import decorators, generics
from rest_framework import permissions, status
from rest_framework.response import Response

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpRequest

from products import permissions as local_permissions
from products import models, serializers
from products import file_handler

from notification.models import Notification



class AllProducts(generics.ListAPIView):
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def list(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, fields={"language": language})
        return Response(serializer.data)


class CreateProduct(generics.CreateAPIView):
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def create(self, request, *args, **kwargs):
        request.data["images"] = self._upload_images(request)
        resp = super().create(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , en_content="a new product added to your specified location"
            , ar_content="تم إضافة خدمة جديدة للفرع المحدد")
        
        return Response(resp.data, status=resp.status_code)
    
    def _upload_images(self, request):
        images_objs = request.FILES.getlist("images")
        self._handling_image_exception(images_objs)
        handler = file_handler.HandleFiles(request)
        images_names = handler.upload_images(images_objs)
        
        return images_names
    
    def _handling_image_exception(self, images_objs):
        """
        handling size and type of images
        """
        for image_obj in images_objs:
            if type(image_obj) != InMemoryUploadedFile:
                raise ValueError(f"images should be an image obj, not {type(image_obj)}")
            
            image_size = image_obj.size // 1024 // 8 / 1024
            if image_size > 3:
                raise ValueError(f"images size should be less than 3 mb")
            
        return True


class RUDProduct(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def retrieve(self, request, *args, **kwargs):
        lanuage = request.META.get("Accept-Language")
        
        instance = self.get_object()
        serializer = self.get_serializer([instance], many=True, fields={"language": lanuage})
        return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_category(request: HttpRequest, pk: int):
    """
    get all products for specific category
    pk here is category_id
    for everybody
    """
    queryset = models.Product.objects.filter(service_provider_location__service_provider__category=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_location(request: HttpRequest, pk: int):
    """
    get all products for specific location
    pk here is location_id
    for everybody
    """
    queryset = models.Product.objects.filter(service_provider_location=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_provider(request: HttpRequest, pk: int):
    """
    get all products for specific service provider
    pk here is service_provider_id
    for everybody
    """
    queryset = models.Product.objects.filter(service_provider_location__service_provider=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

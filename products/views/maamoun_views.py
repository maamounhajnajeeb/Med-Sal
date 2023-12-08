from rest_framework import decorators, generics
from rest_framework import permissions, status
from rest_framework.response import Response

from django.http import HttpRequest

from products import permissions as local_permissions
from products import models, serializers
from products.file_handler import UploadImages, DeleteFiles

from notification.models import Notification



class AllProducts(generics.ListAPIView):
    """
        An api that lists all products
    """
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def list(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, fields={"language": language})
        return Response(serializer.data)


class CreateProduct(generics.CreateAPIView):
    """
        An api that allows to add products 
    """
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def create(self, request, *args, **kwargs):
        new_file_names = self._upload_images(request)
        request.data["images"] = new_file_names
        resp = super().create(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , en_content="a new product added to your specified location"
            , ar_content="تم إضافة خدمة جديدة للفرع المحدد")
        
        return Response(resp.data, status=resp.status_code)
    
    def _upload_images(self, request):
        file_manager = UploadImages(request)
        return file_manager.upload_files("products", request.FILES.getlist("images"))


class RUDProduct(generics.RetrieveUpdateDestroyAPIView):
    """
        An api that allows to Read, Update and Delete a specific product 
        product ID is required 
    """
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def retrieve(self, request, *args, **kwargs):
        lanuage = request.META.get("Accept-Language")
        
        instance = self.get_object()
        serializer = self.get_serializer([instance], many=True, fields={"language": lanuage})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        data = request.data.copy()
        if request.data.get("images"):
            # first delete old ones
            DeleteFiles().delete_files(instance.images)
            # then upload new ones and change names
            file_manager = UploadImages(request)
            data["images"] = file_manager.upload_files("products", request.FILES.getlist("images"))
            
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , en_content="product edited"
            , ar_content="تم تعديل المنتج")
        
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        DeleteFiles().delete_files(instance.images)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=self.request.user.email, receiver_type="Service_Provider"
            , en_content="the product deleted"
            , ar_content="تم حذف المنتج")
        
        instance.delete()


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


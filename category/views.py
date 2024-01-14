from rest_framework import viewsets, decorators
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework import generics

from django.http import HttpRequest

from .serializers import CategorySerializer, CategoryCUDSerializer
from .helpers import searching_func
from .permissions import IsAdmin
from .models import Category

from service_providers.serializers import LocationSerializerSafe
from service_providers.models import ServiceProviderLocations
from notification.models import Notification



@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def parent_sub_category(request, pk: int):
    language = request.META.get("Accept-Language")
    
    queryset = Category.objects.filter(parent=pk)
    serializer = CategorySerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def prime_categories(request):
    language = request.META.get("Accept-Language")
    
    queryset = Category.objects.filter(parent=None)
    serializer = CategorySerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def search_category(request: HttpRequest):
    language = request.META.get("Accept-Language")
    queryset = searching_func(request, language)
    
    if not queryset.exists():
        return Response({
            "message": "There is not result with this search key"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CategorySerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    path : "api/v1/category/"
    this view offers one API method: [GET -> list, retrieve]
    you can call specific category by its id
    """
    
    serializer_class = CategorySerializer
    queryset = Category.objects
    permission_classes = (IsAdmin, )
    
    def get_serializer(self, *args, **kwargs):
        langauge = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", langauge)
        return super().get_serializer(*args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer([self.get_object(), ], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        return Response(
            {"Error": f"Method {self.request.method} is not allowed"}
            , status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def update(self, request, *args, **kwargs):
        return Response(
            {"Error": f"Method {self.request.method} is not allowed"}
            , status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def destroy(self, request, *args, **kwargs):
        return Response(
            {"Error": f"Method {self.request.method} is not allowed"}
            , status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CreateCategoryAPI(generics.CreateAPIView):
    queryset = Category.objects
    permission_classes = (IsAdmin, )
    serializer_class = CategoryCUDSerializer
    
    def get_serializer(self, *args, **kwargs):
        langauge = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", langauge)
        
        return super().get_serializer(*args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="System"
            , en_content=f"{resp.data['en_name']} category added"
            , ar_content=f" تمت إضافة {resp.data['ar_name']}")
        
        return Response(resp.data, status=resp.status_code)

class UpdateCategoryAPI(generics.UpdateAPIView):
    queryset = Category.objects
    permission_classes = (IsAdmin, )
    serializer_class = CategoryCUDSerializer
    
    def get_serializer(self, *args, **kwargs):
        langauge = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", langauge)
        
        return super().get_serializer(*args, **kwargs)
    
    def perform_update(self, serializer):
        instance = serializer.save()
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=self.request.user.email, receiver_type="System"
            , en_content=f"{instance.en_name} category updated"
            , ar_content=f" تم تعديل {instance.ar_name}")

class DestroyCategoryAPI(generics.DestroyAPIView):
    queryset = Category.objects
    permission_classes = (IsAdmin, )
    serializer_class = CategoryCUDSerializer
    
    def get_serializer(self, *args, **kwargs):
        langauge = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", langauge)
        
        return super().get_serializer(*args, **kwargs)
    
    def perform_destroy(self, instance: Category):
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=self.request.user.email, receiver_type="System"
            , en_content=f"{instance.en_name} category deleted"
            , ar_content=f" تم حذف {instance.ar_name}")
        
        return super().perform_destroy(instance)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def category_locations_filter(request: HttpRequest, category_id: int):
    locations = ServiceProviderLocations.objects.filter(service_provider__category=category_id)
    
    serializer = LocationSerializerSafe(locations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

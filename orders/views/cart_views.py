from rest_framework import viewsets, decorators
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpRequest

from typing import Optional

from orders import models, serializers
from utils.permission import authorization



class CartView(viewsets.ModelViewSet):
    serializer_class = serializers.CartSerializer
    queryset = models.CartItems.objects
    
    def list(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True, fields={"language": language})
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        queryset = self.queryset.filter(id=self.kwargs.get("pk"))
        
        if not queryset.exists():
            return Response({"message":"no item exists with this id"})
        
        serializer = self.get_serializer(queryset, many=True, fields = {"language": language})
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        data["patient"] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@decorators.api_view(["GET", ])
@authorization("cartitems")
def user_cart(request: HttpRequest):
    language = request.META.get("Accept-Language")
    
    queryset = models.CartItems.objects.filter(patient=request.user.id)
    serializer = serializers.CartSerializer(queryset, many=True, fields={"language": language})
    
    return Response(serializer.data, status=status.HTTP_200_OK)


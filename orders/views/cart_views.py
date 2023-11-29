from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework import decorators

from django.http import HttpRequest

from orders import permissions as local_permissions
from orders import models, serializers



class CartViewSet(viewsets.ModelViewSet):
    """
    Read, Update, Delete specific Cart element
    Create a Cart Element
    Read all cart Elements for all users
    for admins and authenticated users only
    """
    permission_classes = (local_permissions.HasPermission, )
    queryset = models.Cart.objects
    serializer_class = serializers.CartSerializer
    
    def create(self, request, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        
        data = request.data.copy()
        data["patient"] = request.user.id
        
        serializer = self.serializer_class(data=data, fields={"language": language})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def list(self, request, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.serializer_class(queryset, many=True, fields={"language": language})
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        
        cart_instance = self.queryset.filter(id=int(self.kwargs.get("pk")))
        serializer = self.get_serializer(instance=cart_instance, many=True, fields={"language": language})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, fields={"language": language})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


@decorators.api_view(["GET", ])
@decorators.permission_classes([local_permissions.HasPermission, ])
def user_cart(request: HttpRequest):
    """
    get specific user cart
    need no parameters
    """
    language = request.META.get("Accept-Language")
    
    queryset = models.Cart.objects.filter(patient=request.user.id)
    serializer = serializers.CartSerializer(queryset, many=True, fields={"language": language})
    
    return Response(serializer.data, status=status.HTTP_200_OK)
from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.response import Response

from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language

from .models import Category
from .permissions import IsAdmin
from .serializers import CategorySerializer


class CRUDCategory(viewsets.ModelViewSet):
    
    serializer_class = CategorySerializer
    queryset = Category.objects
    permission_classes = (IsAdmin, )
    
    def check_object_permissions(self, request, obj):
        return super().check_object_permissions(request, obj)


class SerachCategory(generics.ListAPIView):
    pass
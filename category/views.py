from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.response import Response

from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language

from .models import Category
from .serializers import CategorySerializer


class CRUDCategory(viewsets.ModelViewSet):
    
    serializer_class = CategorySerializer
    queryset = Category.objects
    # permission_classes = () # after adding model permission


class SerachCategory(generics.ListAPIView):
    pass
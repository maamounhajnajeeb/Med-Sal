from rest_framework import generics, decorators
from rest_framework.response import Response
from rest_framework import status

from . import serializers, models



class CreateContcatUs(generics.CreateAPIView):
    serializer_class = serializers.ContactUsSerializer
    permission_classes = () # means everybody
    queryset = models.ContactUs.objects
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

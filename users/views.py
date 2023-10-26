from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions, status

from django.http import HttpRequest

from . import models, serializers


class SignUp(generics.CreateAPIView):
    
    permission_classes = ()
    serializer_class = serializers.UsersSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()
        self.encrypt_password(user)
    
    def encrypt_password(self, user):
        user.set_password(user.password)
        user.save()
    
    def get_serializer_class(self):
        assert self.serializer_class is not None, (
            f"'{self.__class__.__name__}' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
        )
        
        user_type = self.request.data["user_type"]
        serializer_model = self.model_mapping(user_type)
        self.serializer_class.Meta.model = serializer_model
        return self.serializer_class
    
    def model_mapping(self, user_type):
        hash_map = {
            "USER": models.Users
            , "ADMIN": models.Admins
            , "SUPER_ADMIN": models.SuperAdmins
        }
        
        return hash_map[user_type]
    
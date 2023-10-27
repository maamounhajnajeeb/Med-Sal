from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions, status

from django.http import HttpRequest

from . import models, serializers


class SignUp(generics.CreateAPIView):
    
    permission_classes = ()
    serializer_class = serializers.UsersSerializer
    
    def create(self, request: HttpRequest, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        return Response({
            "created": "Done"
            , "user_email": resp.data["email"]
            , "user_type": resp.data["user_type"]
            , "token": "the token"
        }, status=resp.status_code
        , headers=self.get_success_headers(resp.data))
    
    def get_serializer_class(self):
        assert self.serializer_class is not None, (
            f"'{self.__class__.__name__}' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
        )
        
        self.change_serializer_model()
        return self.serializer_class
    
    def change_serializer_model(self):
        user_type = self.request.data["user_type"]
        serializer_model = self.model_mapping(user_type)
        self.serializer_class.Meta.model = serializer_model
    
    def model_mapping(self, user_type):
        hash_map = {
            "USER": models.Users
            , "ADMIN": models.Admins
            , "SUPER_ADMIN": models.SuperAdmins
        }
        return hash_map[user_type]
    
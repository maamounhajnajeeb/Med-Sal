from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes

from django.http import HttpRequest

from rest_framework_simplejwt.tokens import RefreshToken

from . import models, serializers


class SignUp(generics.CreateAPIView):
    
    permission_classes = ()
    serializer_class = serializers.UsersSerializer
    
    def create(self, request: HttpRequest, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        token = RefreshToken.for_user(user_instance)
        return Response({
            "created": "Done"
            , "user_email": serializer.data["email"]
            , "user_type": serializer.data["user_type"]
            , "tokens": {
                "refresh": str(token)
                , "access": str(token.access_token)
            }
        }, status=status.HTTP_201_CREATED
        , headers=headers)
    
    def perform_create(self, serializer):
        user_instance = serializer.save()
        return user_instance
    
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
            , "SERVICE_PROVIDER": models.Users
            , "ADMIN": models.Admins
            , "SUPER_ADMIN": models.SuperAdmins
        }
        return hash_map[user_type]


@api_view(http_method_names=['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def hi(request):
    return Response({"hello": "man"})


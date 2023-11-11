from django.contrib.auth import get_user_model
from django.http import HttpRequest

from rest_framework import permissions, decorators
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework import views

from rest_framework_simplejwt.views import TokenObtainPairView

import os

from . import serializers, helpers
from . import models, permissions as local_permissions


Users = get_user_model()


class ListAllUsers(generics.ListAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAdminUser, ) # Admin is_staff only
    queryset = Users.objects


class UsersView(generics.RetrieveUpdateDestroyAPIView):
    """
    general retrieve, update, destroy api
    not for updating email of password
    """
    serializer_class = serializers.SpecificUserSerializer
    permission_classes = (local_permissions.IsAdminOrOwner, )
    queryset = Users.objects
    
    def update(self, request, *args, **kwargs):
        if request.data.get("image"):
            image_path = request.user.image.path
            if os.path.exists(image_path):
                os.remove(image_path)
                
        return super().update(request, *args, **kwargs)


class ServiceProviderRegister(views.APIView):
    """
    Signing Up service providers only
    """
    serializer_class = serializers.ServiceProviderSerializer
    permission_classes = (permissions.AllowAny, )
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def create(self, request: HttpRequest, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_instance = serializer.save()
        
        confirm = helpers.SendMail(
            to=user_instance[0], request=request
            , view="/api/v1/users/email_confirmation/")
        confirm.send_mail()
        
        models.EmailConfirmation.objects.create(
            user_id=user_instance[1], token=confirm.token)
        
        return Response({
            "message": "Confirmation email sent"
        , }, status=status.HTTP_201_CREATED)


class SignUp(generics.CreateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.AllowAny, )
    queryset = Users.objects
    
    def create(self, request: HttpRequest, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        
        confirm = helpers.SendMail(
            to=resp.data.get("email"), request=request
            , view="/api/v1/users/email_confirmation/")
        confirm.send_mail()
        
        models.EmailConfirmation.objects.create(
            user_id=resp.data.get("id"), token=confirm.token)
        
        return Response({
            "message": "Confirmation email sent"
        , }, status=resp.status_code
        , headers=self.get_success_headers(resp.data))


@decorators.api_view(["GET"])
def email_confirmation(request: HttpRequest, token: str):
    query = models.EmailConfirmation.objects.filter(token=token)
    
    if not query.exists():
        return Response(
            {"message": "Invalid email confirmation token"}
            , status=status.HTTP_404_NOT_FOUND)
    
    confirm_record = query.first()
    helpers.activate_user(confirm_record.user_id)
    
    query.first().delete()
    return Response(
        {"message": "Valid email you can log in now"}
        , status=status.HTTP_202_ACCEPTED)


@decorators.api_view(["POST", ])
@decorators.permission_classes((permissions.IsAuthenticated, ))
def change_email(request: HttpRequest):
    user_id = request.user.id
    new_email = request.data.get("new_email")
    
    confirm = helpers.SendMail(
        to=new_email, request=request
        , view="/api/v1/users/accept_new_email/")
    confirm.send_mail()
    
    models.EmailChange.objects.create(
        user_id=user_id, new_email=new_email, token=confirm.token)
    
    return Response({
        "message": "confirmation message sent to your new email"
    }, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes((permissions.IsAuthenticated, ))
def accept_email_change(request: HttpRequest, token: str):
    query = models.EmailChange.objects.filter(token=token)
    if not query.exists():
        return Response({
            "message": "Invalid confirmation link or expired"
        }, status=status.HTTP_404_NOT_FOUND)
    
    confirm_record = query.first()
    helpers.change_user_email(
        id=confirm_record.user_id
        , new_email=confirm_record.new_email)
    
    query.first().delete()
    
    return Response({
        "message": "user email changed successfully"
    }, status=status.HTTP_202_ACCEPTED)


class LogIn(TokenObtainPairView):
    """
    login view
    just editing the main login to add user(id, user_type) in the serializer
    """
    serializer_class = serializers.LogInSerializer

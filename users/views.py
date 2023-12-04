from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import HttpRequest

from rest_framework import permissions, decorators
from rest_framework.response import Response
from rest_framework import status, generics

from rest_framework_simplejwt.views import TokenObtainPairView

import os

from . import serializers, helpers
from . import models, permissions as local_permissions
from . import throttles as local_throttles

from service_providers.models import ServiceProvider
from utils.permission import authorization_with_method, HasPermission

Users = get_user_model()


@decorators.api_view(["GET", ])
@authorization_with_method("list", "users")
def list_all_users(request: HttpRequest):
    """
    get all users and show them to admins
    """
    queryset = Users.objects.all()
    serializer = serializers.UserSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#
class UsersView(generics.RetrieveUpdateDestroyAPIView):
    """
    general retrieve, update, destroy api for profile owners and admins
    not for updating email or password
    """
    serializer_class = serializers.SpecificUserSerializer
    permission_classes = (HasPermission, )
    queryset = Users.objects
    
    def get_permissions(self):
        return [permission("users") for permission in self.permission_classes]
    
    def update(self, request, *args, **kwargs):
        if request.data.get("image"):
            image_path = request.user.image.path
            helpers.delete_image(image_path)
        return super().update(request, *args, **kwargs)
    
    def perform_destroy(self, instance: Users):
        image_path = instance.image.path
        helpers.delete_image(image_path)
        instance.delete()


class ServiceProviderList(generics.ListAPIView):
    """
    showing service providers list for admins only
    """
    serializer_class = serializers.ServiceProviderSerializer
    queryset = ServiceProvider.objects
    permission_classes = ( )


class ServiceProviderCreate(generics.CreateAPIView):
    """
    signing up service providers for everybody
    """
    serializer_class = serializers.ServiceProviderSerializer
    queryset = ServiceProvider.objects
    permission_classes = (local_permissions.UnAuthenticated, )
    
    def create(self, request: HttpRequest, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        pk, email = resp.data["user"]["id"], resp.data["user"]["email"]
        
        confirm = helpers.SendMail(
            to=email, request=request, out=True
            , view="/api/v1/users/email_confirmation/")
        confirm.send_mail()
        
        models.EmailConfirmation.objects.create(
            user_id=pk, email=email, ip_address=self.request.META.get("REMOTE_ADDR"))
        
        return Response({
            "message": f"Confirmation email sent to: {email}"
        , }, status=status.HTTP_201_CREATED)


class ServiceProviderRUD(generics.RetrieveUpdateDestroyAPIView):
    """
    Read, Delete, Update specific service provider
    """
    serializer_class = serializers.ServiceProviderSerializer
    queryset = ServiceProvider.objects
    permission_classes = (
        permissions.IsAuthenticated, local_permissions.HavePermission, )
    
    def update(self, request, *args, **kwargs):
        if request.data.get("user"):
            self.update_user_instance()
        
        return super().update(request, *args, **kwargs)
    
    def update_user_instance(self):
        """
        updating the user_instance in the service_provider record
        """
        request_data = self.request.data.copy()
        user_data = request_data.pop("user", None)
        if user_data:
            pk = self.kwargs.get("pk")
            user_instance = Users.objects.filter(pk=pk)
            if user_data.get("image"):
                imag_path = user_instance.image.path
                os.remove(imag_path)
            user_instance.update(**user_data)
    
    def perform_destroy(self, instance):
        """
        remove files from the media folder before destroying record
        """
        def delete_file(file):
            try:
                os.remove(file.path)
                print("Image Deleted")
            except:
                print("No Image")
        
        delete_file(instance.user.image)
        delete_file(instance.provider_file)
        
        return super().perform_destroy(instance)

# 
class SignUp(generics.CreateAPIView):
    """
    sign up as user, admin, and super_admin
    """
    serializer_class = serializers.UserSerializer
    permission_classes = (local_permissions.UnAuthenticated, )
    queryset = Users.objects
    
    def create(self, request: HttpRequest, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        
        confirm = helpers.SendMail(
            to=resp.data.get("email"), request=request, out=True
            , view="/api/v1/users/email_confirmation/")
        confirm.send_mail()
        
        models.EmailConfirmation.objects.create(
            user_id=resp.data.get("id"), email=resp.data.get("email")
            , ip_address=self.request.META.get("REMOTE_ADDR"))
        
        return Response({
            "message": "Confirmation email sent"
        , }, status=resp.status_code
        , headers=self.get_success_headers(resp.data))

# 
@decorators.api_view(["GET"])
@decorators.permission_classes([local_permissions.UnAuthenticated, ])
def email_confirmation(request: HttpRequest):
    """
    this function is to use after sign up for confirmation email confirmation puprose
    """
    ip_address = request.META.get("REMOTE_ADDR")
    query = models.EmailConfirmation.objects.filter(ip_address=ip_address)
    
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
@decorators.permission_classes([local_permissions.UnAuthenticated, ])
@decorators.throttle_classes([local_throttles.UnAuthenticatedRateThrottle, ])
def resend_email_validation(request: HttpRequest):
    """
    this function is used when email_confirmation failed to send email
    """
    ip_address = request.META.get("REMOTE_ADDR")
    query = models.EmailConfirmation.objects.filter(ip_address=ip_address)
    
    if not query.exists():
        return Response(
            {"message": "Invalid Ip Address, there is no associated account with this IP"}
            , status=status.HTTP_404_NOT_FOUND)
    
    confirm_record = query.first()
    confirm = helpers.SendMail(
        to=confirm_record.email, request=request, out=True
        , view="/api/v1/users/email_confirmation/")
    confirm.send_mail()
    
    return Response(
        {"message": "Confirmation email resent"}
        , status=status.HTTP_202_ACCEPTED)


@decorators.api_view(["POST", ])
@decorators.permission_classes((permissions.IsAuthenticated, ))
def change_email(request: HttpRequest):
    """
    give authenticated user ability to change its email
    send a confirmation message to the new email.
    """
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
    """
    check if the link sent to email is real
    and make the new email official email for user
    """
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

#
@decorators.api_view(["POST", ])
def check_password(request: HttpRequest):
    """
    first step to change password to authenticated users
    """
    pwd, re_pwd = request.data.get("password"), request.data.get("re_password")
    if pwd != re_pwd:
        return Response({
            "message": "Password fields are not the same"
        }, status=status.HTTP_409_CONFLICT)
    
    user_email = request.user.email
    match = authenticate(email=user_email, password=pwd)
    if not match:
        return Response({
            "message": "The passowrd inputed isn't same authenticated user password"
        }, status=status.HTTP_409_CONFLICT)
    
    return Response({
        "message": "Valid passwords you can go to change password"
    }, status=status.HTTP_202_ACCEPTED)

#
@decorators.api_view(["POST", ])
def change_password(request: HttpRequest):
    """
    second step to change password to authenticated users
    """
    new_pwd = request.data.get("new_password")
    helpers.set_password(request.user, new_pwd)
    
    return Response({
        "message": "Password changed successfully"
    }, status=status.HTTP_202_ACCEPTED)

#
@decorators.api_view(["POST", ])
@decorators.permission_classes([local_permissions.UnAuthenticated, ])
def reset_password(request: HttpRequest):
    """
    first step to unauthenticated users to reset there password
    it send an email with a 6 digits code
    """
    email = request.data.get("email")
    user_instance = Users.objects.filter(email=email)
    if not user_instance.exists():
        return Response({
            "message": "There is no account associated with this email"
        }, status=status.HTTP_404_NOT_FOUND)
    
    code = helpers.generate_code()
    ip_address = request.META.get("REMOTE_ADDR")
    models.PasswordReset.objects.create(
        code=code, user=user_instance.first(), ip_address=ip_address)
    
    send_mail(subject="Password Reset"
        , message=f"put this code: {code} in the input field"
        , from_email="med-sal-adminstration@gmail.com"
        , recipient_list=[email, ])
    
    return Response({
        "message": "A 6 numbers code sent to your mail, check it"
    }, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([local_permissions.UnAuthenticated, ])
@decorators.throttle_classes([local_throttles.UnAuthenticatedRateThrottle, ])
def resend_code(request: HttpRequest):
    ip_address = request.META.get("REMOTE_ADDR")
    record = models.PasswordReset.objects.filter(ip_address=ip_address)
    
    if not record.exists():
        return Response({
            "message": "We've not send an code for this specific email"
        }, status=status.HTTP_404_NOT_FOUND)
    
    record = record.select_related("user").first()
    send_mail(subject="Password Reset"
        , message=f"put this code: {record.code} in the input field"
        , from_email="med-sal-adminstration@gmail.com"
        , recipient_list=[record.user.email, ])
    
    return Response({
        "message": "A 6 numbers code sent to your mail, check it"
    }, status=status.HTTP_200_OK)

#
@decorators.api_view(["POST", ])
@decorators.permission_classes([local_permissions.UnAuthenticated, ])
def enter_code(request):
    """
    second step
    check if the inputed code the same
    and depending on that it giv user ability to write new password
    """
    code = request.data.get("code")
    
    record = models.PasswordReset.objects.filter(code=code)
    if not record.exists():
        return Response({
            "message": "sorry, but there is no code like this in the database, try to reset password again"
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        "message":"Right code, you can put new password now"
    }, status=status.HTTP_202_ACCEPTED)

#
@decorators.api_view(["POST", ])
@decorators.permission_classes([local_permissions.UnAuthenticated, ])
def new_password(request: HttpRequest):
    """
    third step
    saving the new password to user record if every scenario goes will
    """
    pwd, re_pwd = request.data.get("password"), request.data.get("re_password")
    if pwd != re_pwd:
        return Response({
            "message": "Password fields are not the same"
        }, status=status.HTTP_409_CONFLICT)
    
    ip_address = request.META.get("REMOTE_ADDR")
    record = models.PasswordReset.objects.select_related("user").get(ip_address=ip_address)
    user = record.user
    user.password = make_password(pwd)
    user.save()
    
    record.delete()
    
    return Response({
        "message": "Password changed successfully, now you can log in with the new password"
    }, status=status.HTTP_202_ACCEPTED)

#
class LogIn(TokenObtainPairView):
    """
    login view
    just editing the main login to add user(id, user_type) in the serializer
    """
    serializer_class = serializers.LogInSerializer
    permission_classes = (local_permissions.UnAuthenticated, )
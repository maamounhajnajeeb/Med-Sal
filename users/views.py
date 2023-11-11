from django.contrib.auth import get_user_model
from django.http import HttpRequest

from rest_framework import permissions, decorators
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework import views

from rest_framework_simplejwt.views import TokenObtainPairView

from . import serializers, helpers
from . import models



Users = get_user_model()


class ListAllUsers(generics.ListAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAdminUser, ) # Admin is_staff only
    queryset = Users.objects


class UsersView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = Users.objects


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
        
        confirm = helpers.SendMail(to=user_instance[0], request=request)
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
        
        confirm = helpers.SendMail(to=resp.data.get("email"), request=request)
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


class LogIn(TokenObtainPairView):
    """
    login view
    just editing the main login to add user(id, user_type) in the serializer
    """
    serializer_class = serializers.LogInSerializer

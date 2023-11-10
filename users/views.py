from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework import permissions, decorators

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import serializers, helpers
from . import models
from category.models import Category
from service_providers.models import ServiceProvider
from service_providers.serializers import ServiceProviderSerializer



Users = get_user_model()


class ListAllUsers(generics.ListAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAdminUser, ) # Admin is_staff only
    queryset = Users.objects


class UsersView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = Users.objects


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


@decorators.api_view(["POST"])
def email_confirmation(request: HttpRequest, token: str):
    query = models.EmailConfirmation.objects.filter(token=token)
    
    if not query.exists():
        return Response(
            {"message": "Invalid email confirmation token"}
            , status=status.HTTP_404_NOT_FOUND)
    
    user = query.first()
    helpers.activate_user(user.id)
    
    query.first().delete()
    return Response(
        {"message": "Valid email you can log in now"}
        , status=status.HTTP_202_ACCEPTED)


@decorators.api_view(["POST"])
def register(request):
    serializer = serializers.UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    
    category = Category.objects.get(id=request.data.get("category"))
    ServiceProvider.objects.create(
        category=category, user=user
        , iban=request.data.get("iban")
        , bank_name=request.data.get("bank_name")
        , swift_code=request.data.get("swift_code")
        , provider_file=request.data.get("provider_file")
        , business_name=request.data.get("business_name")
        )
    
    return Response({"message": "done"}, status=status.HTTP_201_CREATED)


class ServiceProviderRegister(generics.CreateAPIView):
    permission_classes = ( )
    serializer_class = serializers.ServiceProviderSerializer
    queryset = Users.objects


@decorators.api_view(["POST", ])
def login(request):
    email, password = request.data.get("email"), request.data.get("password")
    user = authenticate(email=email, password=password)
    if user is not None:
        token = RefreshToken.for_user(user)
        return Response({
            "access": str(token.access_token)
            , "refresh": str(token)
        }, status=status.HTTP_202_ACCEPTED)
    
    return Response({
        "message": "Invalid user credentials"
    }, status=status.HTTP_404_NOT_FOUND)


# resend 2FA code
# class ResendActivationCodeView(APIView):
#     def post(self, request):
#         email = request.data.get("email")

#         if not email:
#             return Response(
#                 {"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             user = Users.objects.get(email=email, is_active=False)
#         except Users.DoesNotExist:
#             return Response(
#                 {"message": "User not found or already activated."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         activation_code = user.generate_verification_code()

#         # Send the new activation code via email
#         email_subject = "2FA Code for Activation"
#         email_message = f"Your new 2FA code for activation is: {activation_code}"
#         send_mail(email_subject, email_message, "your@email.com", [user.email])

#         return Response(
#             {"message": "Activation code sent successfully."}, status=status.HTTP_200_OK
#         )


# # activate user code
# class Activate2FAView(APIView):
#     def post(self, request):
#         code = request.data.get("code")  # Get the 2FA code from the request data

#         # Get the user ID from the cookie
#         user_id = request.COOKIES.get("user_id")

#         if not user_id:
#             return Response(
#                 {"message": "User ID not found in cookie."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             user = Users.objects.get(id=user_id)
#         except Users.DoesNotExist:
#             return Response(
#                 {"message": "User not found."}, status=status.HTTP_404_NOT_FOUND
#             )

#         if user.verify_two_factor_code(code):
#             # Check if the provided code is valid and within the time frame
#             user.email_confirmed = True
#             user.is_active = True
#             user.save()
#             return Response(
#                 {"message": "User activated successfully."}, status=status.HTTP_200_OK
#             )
#         else:
#             return Response(
#                 {"message": "Invalid 2FA code or code has expired."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )


# # login ....
# class CustomTokenObtainPairView(TokenObtainPairView):
#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
        
#         if response.status_code == status.HTTP_200_OK:
#             # If the login was successful, customize the response
#             user = Users.objects.get(email=request.data["email"])
#             user_type = user.user_type
#             refresh = RefreshToken.for_user(user)
            
#             response.data["message"] = "Login successful"
#             response.data["user_type"] = str(user_type)
#             # response.data["tokens"] = {"access": str(refresh), "refresh": str(refresh.access_token)}
            
#         return response


# # Refreash token
# class CustomTokenRefreshView(TokenRefreshView):
#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
        
#         if response.status_code == status.HTTP_200_OK:
#             response.data["message"] = "Token refreshed successfully"
        
#         return response

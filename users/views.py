from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from djoser.views import UserViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Users
# from django.contrib.auth import get_user_model
# User = get_user_model()
from category.models import Category
from .serializers import UserRegistrationSerializer
from service_providers.models import ServiceProvider


# users : create 
class CustomUserViewSet(UserViewSet):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny, )
    http_method_names = ["get", "post", "patch", "put", "delete"]
    
    def create(self, request, *args, **kwargs):
        user_data = request.data
        
        response = super().create(request, *args, **kwargs)# default register
        if response.data["user_type"] != Users.Types.SERVICE_PROVIDER:
            return Response(response.data, status=response.status_code)
        
        # 1] Fetch the Category id from user_data 2] and get user_id from register response data
        prov_data = response.data
        prov_id = prov_data.get("id")
        
        category_value = user_data.get("category")
        category_instance = get_object_or_404(Category, id=category_value)
        
        service_prov_data = self.create_service_provider(prov_id, category_instance, prov_data)
        
        return Response(service_prov_data, status=response.status_code)
    
    def create_service_provider(self, prov_id: int, category: Category, prov_data: dict):
        service_prov_instance = ServiceProvider.objects.create(
            user_id=prov_id
            , business_name=prov_data.get("business_name")
            , contact_number=prov_data.get("contact_number")
            , bank_name=prov_data.get("bank_name")
            , category=category, iban=prov_data.get("iban")
            , swift_code=prov_data.get("swift_code")
        )
        
        return service_prov_instance


# resend 2FA code
class ResendActivationCodeView(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = Users.objects.get(email=email, is_active=False)
        except Users.DoesNotExist:
            return Response(
                {"message": "User not found or already activated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        activation_code = user.generate_verification_code()

        # Send the new activation code via email
        email_subject = "2FA Code for Activation"
        email_message = f"Your new 2FA code for activation is: {activation_code}"
        send_mail(email_subject, email_message, "your@email.com", [user.email])

        return Response(
            {"message": "Activation code sent successfully."}, status=status.HTTP_200_OK
        )


# activate user code
class Activate2FAView(APIView):
    def post(self, request):
        code = request.data.get("code")  # Get the 2FA code from the request data

        # Get the user ID from the cookie
        user_id = request.COOKIES.get("user_id")

        if not user_id:
            return Response(
                {"message": "User ID not found in cookie."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response(
                {"message": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if user.verify_two_factor_code(code):
            # Check if the provided code is valid and within the time frame
            user.email_confirmed = True
            user.is_active = True
            user.save()
            return Response(
                {"message": "User activated successfully."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Invalid 2FA code or code has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# login ....
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            # If the login was successful, customize the response
            user = Users.objects.get(email=request.data["email"])
            user_type = user.user_type
            refresh = RefreshToken.for_user(user)
            
            response.data["message"] = "Login successful"
            response.data["user_type"] = str(user_type)
            # response.data["tokens"] = {"access": str(refresh), "refresh": str(refresh.access_token)}
            
        return response


# Refreash token
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            response.data["message"] = "Token refreshed successfully"
        
        return response

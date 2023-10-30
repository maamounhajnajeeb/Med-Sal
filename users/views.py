from djoser.views import UserViewSet
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from .serializers import UserRegistrationSerializer
from .models import Users
from service_providers.models import ServiceProvider
from rest_framework import status
from rest_framework.response import Response
<<<<<<< HEAD
from rest_framework import generics
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
=======
from rest_framework.permissions import AllowAny
from category.models import Category
>>>>>>> 2fdb9f7c5f6430580c04aef87337da0a97069d11

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

<<<<<<< HEAD
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

=======
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


# users : create ......
class CustomUserViewSet(UserViewSet):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    http_method_names = ["get", "post", "patch", "put", "delete"]

    def create(self, request):
        user_data = request.data
        user_type = user_data.get("user_type")

        if user_type == Users.Types.SERVICE_PROVIDER:
            response = super().create(request)

            # Check if the user was created successfully
            if response.status_code == status.HTTP_201_CREATED:
                super_user = response.data
                super_user_id = super_user["id"]

                # Fetch the Category instance based on the user_data value
                category_value = user_data.get("category")
                category_instance = get_object_or_404(Category, name=category_value)

                ServiceProvider.objects.create(
                    user_id=super_user_id,
                    business_name=user_data.get("business_name"),
                    contact_number=user_data.get("contact_number"),
                    bank_name=user_data.get("bank_name"),
                    category=category_instance,
                    iban=user_data.get("iban"),
                    swift_code=user_data.get("swift_code"),
                )

                return Response(super_user, status=status.HTTP_201_CREATED)
            else:
                return response

        try:
            response = super().create(request)
            if (
                response.status_code == status.HTTP_400_BAD_REQUEST
                and "Unable to create account." in response.data
            ):
                return Response(
                    {"error": "Failed to create the account."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
            response.data["refresh"] = str(refresh)
            response.data["access"] = str(refresh.access_token)

        return response


# Refreash token
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            response.data["message"] = "Token refreshed successfully"

        return response
>>>>>>> 2fdb9f7c5f6430580c04aef87337da0a97069d11

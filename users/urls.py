from django.urls import path

from rest_framework_simplejwt.views import TokenObtainSlidingView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
    , )

from . import views


app_name = "users"

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="sign_up"),
    path("service_provider_register/", views.register, name="service_provider_register"),
    path("email_confirmation/<str:token>", views.email_confirmation, name="email_confirmation"),
    
    path('login/', views.login, name='login'),
    path('refresh_token/', TokenRefreshView.as_view(), name='token_refresh'),

    
    # list users
    # path("users/all/", CustomUserViewSet.as_view({"get": "list"}), name="list-users"),
    
    # register users and service provider
    # path("users/register/", CustomUserViewSet.as_view({"post": "create", "get": "list"}), name="user-registration"),
    
    # login
    # path("users/login/", CustomTokenObtainPairView.as_view(), name="jwt-create"),
    # path("users/refresh/", CustomTokenRefreshView.as_view(), name="jwt-refresh"),
    # path("", include("djoser.urls")),
    # path("", include("djoser.urls.jwt")),
    
    # # resend code
    # path("users/resend-activation/", ResendActivationCodeView.as_view(), name="resend-activation"),
    
    # # 2FA
    # path("users/activate-2fa/", Activate2FAView.as_view(), name="activate-2fa"),
]

# avtivate user on  (api/v1/users/activation/)
# resend activation email  (api/v1/users/resend_activation/)
# update user information and delete (api/v1/users/me/)
# authenticated set password   (api/v1/users/set_password/)
# not authenticated CHANGE password  (api/v1/users/reset_password/)  and then confirm (api/users/reset_password_confirm/)

from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from . import views


app_name = "users"

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="sign_up"),
    path("service_provider_register/", views.ServiceProviderRegister.as_view(), name="service_provider_register"),
    path("email_confirmation/<str:token>", views.email_confirmation, name="email_confirmation"),
    
    path("all/", views.ListAllUsers.as_view(), name="all users"),
    
    path('login/', views.LogIn.as_view(), name='login'),
    path('refresh_token/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # # resend code
    # path("users/resend-activation/", ResendActivationCodeView.as_view(), name="resend-activation"),
    
    # # 2FA
    # path("users/activate-2fa/", Activate2FAView.as_view(), name="activate-2fa"),
]

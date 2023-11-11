from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from . import views


app_name = "users"

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="sign_up"),
    path("service_provider_register/", views.ServiceProviderRegister.as_view(), name="service_provider_register"),
    
    path("email_confirmation/<str:token>", views.email_confirmation, name="email_confirmation"),
    path("change_email/", views.change_email, name="email_change"),
    path("accept_new_email/<str:token>", views.accept_email_change, name="accept_email_changing"),
    
    path("all/", views.ListAllUsers.as_view(), name="all_users"),
    path("<int:pk>/", views.UsersView.as_view(), name="specific_user"),
    
    path('login/', views.LogIn.as_view(), name='login'),
    path('refresh_token/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # # resend code
    # path("users/resend-activation/", ResendActivationCodeView.as_view(), name="resend-activation"),
    
    # # 2FA
    # path("users/activate-2fa/", Activate2FAView.as_view(), name="activate-2fa"),
]

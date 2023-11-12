from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from . import views


app_name = "users"

urlpatterns = [
    # not authenticated
    path("signup/", views.SignUp.as_view(), name="sign_up"),
    path("service_provider_register/", views.ServiceProviderRegister.as_view(), name="service_provider_register"),
    
    # not authenticated
    path("email_confirmation/", views.email_confirmation, name="email_confirmation"),
    path("resend_email_validation/", views.resend_email_validation, name="resend_email_validation"),
    
    # authenticated
    path("accept_new_email/<str:token>", views.accept_email_change, name="accept_email_changing"),
    path("change_email/", views.change_email, name="email_change"),
    
    # authenticated
    path("check_password/", views.check_password, name="check_password"),
    path("change_password/", views.change_password, name="change_password"),
    
    # not authenticated
    path("reset_password/", views.reset_password, name="reset_password"),
    path("enter_code/", views.enter_code, name="enter_code"),
    path("new_password/", views.new_password, name="new_password"),
    
    path("all/", views.ListAllUsers.as_view(), name="all_users"),
    path("<int:pk>/", views.UsersView.as_view(), name="specific_user"),
    
    path('login/', views.LogIn.as_view(), name='login'),
    path('refresh_token/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # # resend code
    # path("users/resend-activation/", ResendActivationCodeView.as_view(), name="resend-activation"),
    
    # # 2FA
    # path("users/activate-2fa/", Activate2FAView.as_view(), name="activate-2fa"),
]

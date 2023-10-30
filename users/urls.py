from django.urls import path, include

# from .views import CustomTokenCreateView

# from djoser.views import UserCreateView
from .views import (
    CustomUserViewSet,
    CustomTokenObtainPairView,
    ResendActivationCodeView,
    Activate2FAView,
    CustomTokenRefreshView,
)


app_name = "users"


urlpatterns = [
<<<<<<< HEAD
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("sign_up/", views.SignUp.as_view(), name="sign_up"),
    path("test_cred/", views.hi, name="hi")
=======
    # list users
    path("users/", CustomUserViewSet.as_view({"get": "list"}), name="list-users"),
    # register users and service provider
    path(
        "register/",
        CustomUserViewSet.as_view({"post": "create", "get": "list"}),
        name="user-registration",
    ),
    # login
    path("login/", CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="jwt-refresh"),
    path("", include("djoser.urls")),
    path("", include("djoser.urls.jwt")),
    # resend code
    path(
        "resend-activation/",
        ResendActivationCodeView.as_view(),
        name="resend-activation",
    ),
    # 2FA
    path("activate-2fa/", Activate2FAView.as_view(), name="activate-2fa"),
    # avtivate user on  (api/users/activation/)
    # resend activation email  (api/users/resend_activation/)
    # update user information and delete   (api/users/me/)
    # set password   (api/users/set_password/)
    # CHANGE password  (api/users/reset_password/)  and then confirm (api/users/reset_password_confirm/)
>>>>>>> 2fdb9f7c5f6430580c04aef87337da0a97069d11
]

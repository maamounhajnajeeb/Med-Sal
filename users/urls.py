from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = "users"

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("sign_up/", views.SignUp.as_view(), name="sign_up"),
    path("test_cred/", views.hi, name="hi")
]

from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from category.views import CategoryGet

app_name = "category"

urlpatterns = [
    path('testing_category/', CategoryGet.as_view())
]

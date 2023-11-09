from rest_framework.routers import DefaultRouter
from django.urls import path, include

from service_providers import views


# from core urls: api/v1/service_providers/

app_name = "serivce_providers"

router = DefaultRouter()
router.register("", views.CRUDServiceProviders, basename='providers_crud')

urlpatterns = [
    # path('', router.urls, name="provider_crud"),
    path('location', views.locationss)
]

urlpatterns += router.urls
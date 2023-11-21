from rest_framework.routers import DefaultRouter
from django.urls import path

from service_providers import views


# from core urls: api/v1/service_providers/

app_name = "serivce_providers"

router = DefaultRouter()
# router.register("", views.CRUDServiceProviders, basename='providers_crud') # Tareq

router.register("profile/update_requests", views.ServiceProviderUpdateRequestViewSet, basename='update_requests_crud')

urlpatterns = [
]

urlpatterns += router.urls

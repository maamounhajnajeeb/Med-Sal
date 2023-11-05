from rest_framework.routers import DefaultRouter
from django.urls import path, include

from service_providers.views import *


app_name = "serivce_providers"

router = DefaultRouter()
router.register("", CRUDServiceProviders, basename = 'service_providers')

urlpatterns = [

    path('', include(router.urls)),

    path('location', locationss)
]

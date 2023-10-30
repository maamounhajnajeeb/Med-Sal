from rest_framework import routers

from django.urls import path

from . import views

app_name = "category"

router = routers.SimpleRouter()
router.register("", views.CRUDCategory, basename="category-functionality")

urlpatterns = [
    
]

urlpatterns += router.urls

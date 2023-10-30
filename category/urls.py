from rest_framework import routers

from django.urls import path, include

from . import views

app_name = "category"

router = routers.SimpleRouter()
router.register("", views.CRUDCategory, basename="category-functionality")

urlpatterns = [
    path("home/", views.home, name="home"),
]

urlpatterns += router.urls

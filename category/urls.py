from rest_framework import routers

from django.urls import path, include

from . import views

app_name = "category"

router = routers.SimpleRouter()
router.register("", views.CRUDCategory, basename="category-functionality")
# router.register("translations/testing", views.MyCategoryView, basename="translation-functionality")

urlpatterns = [
    path("home/", views.home, name="home"),
    path("language/change/", views.change_lang, name="change_lang"),
]

urlpatterns += router.urls

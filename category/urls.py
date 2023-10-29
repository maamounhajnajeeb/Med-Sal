from rest_framework import routers

from django.urls import path

from . import views

app_name = "category"

router = routers.SimpleRouter()
router.register("", views.CRUDCategory, basename="category-functionality")

urlpatterns = [
    path("search/", views.SerachCategory.as_view(), name="search_for_category"),
]

urlpatterns += router.urls

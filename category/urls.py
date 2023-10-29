from rest_framework import routers

from django.urls import path

from . import views

app_name = "category"

router = routers.SimpleRouter()
router.register("", views.CRUDCategory, basename="all_categories")

urlpatterns = [
    # path("all_categories/", views.CRUDCategory.as_view(), name="all_categories"),
]

urlpatterns += router.urls
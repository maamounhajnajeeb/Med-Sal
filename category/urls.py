from rest_framework import routers

from django.urls import path

from . import views

app_name = "category"

router = routers.SimpleRouter()
router.register("category", views.CRUDCategory, basename="category-functionality")

urlpatterns = [
    path("sub_category/<int:pk>/", views.parent_sub_category, name="parent_sub_category"),
]

urlpatterns += router.urls

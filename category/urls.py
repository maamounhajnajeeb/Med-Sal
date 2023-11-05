from rest_framework import routers

from django.urls import path

from . import views

app_name = "category"

router = routers.SimpleRouter()
router.register("", views.CRUDCategory, basename="category-functionality")

urlpatterns = [
    path("sub_category/<int:pk>/", views.parent_sub_category, name="parent_sub_category"),
    path("search/<str:name>/", views.search_category, name="search_category"),
]

urlpatterns += router.urls

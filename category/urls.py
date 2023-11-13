from rest_framework import routers

from django.urls import path

from . import views

app_name = "category"

router = routers.SimpleRouter()
router.register("", views.CategoryViewSet, basename="category-functionality")

urlpatterns = [
    path("sub_categories/<int:pk>/", views.parent_sub_category, name="parent_sub_category"),
    path("prime_categories/", views.prime_categories, name="parent_sub_category"),
    path('search/', views.search_category, name="search_category"), # ?query=......
]

urlpatterns += router.urls

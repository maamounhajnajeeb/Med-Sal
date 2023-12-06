from rest_framework import routers

from django.urls import path

from . import views, tareq_views

app_name = "category"

router = routers.SimpleRouter()
router.register("", views.CategoryViewSet, basename="category-functionality")

urlpatterns = [
    path("sub_categories/<int:pk>/", views.parent_sub_category, name="parent_sub_category"),
    path("prime_categories/", views.prime_categories, name="parent_sub_category"),
    path('search/', views.search_category, name="search_category"), # ?query=......
    
    # get providers locations by category
    path("locations/<int:category_id>/", views.category_locations_filter, name="category_locations_filter"),
        
    # Get only list of doctors   
    path("doctors/", tareq_views.doctor_category_filter, name="doctors_filter")
]

urlpatterns += router.urls

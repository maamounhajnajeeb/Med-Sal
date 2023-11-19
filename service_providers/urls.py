from rest_framework.routers import DefaultRouter
from django.urls import path, include

from service_providers import views


# from core urls: api/v1/service_providers/

app_name = "serivce_providers"

router = DefaultRouter()
router.register("", views.CRUDServiceProviders, basename='providers_crud')

urlpatterns = [
    path('profile/update_data/', views.ServiceProviderUpdateRequestCreateAPI.as_view(), ),
    path('profile/approve_request/<int:pk>/', views.ServiceProviderApproveAPI.as_view()),

    # path('location', Location.as_view()),
    
    # path('distance', ServiceProviderDistanceListView.as_view())
]

urlpatterns += router.urls
from rest_framework.routers import DefaultRouter
from django.urls import path

from service_providers import views
from service_providers import maamoun_view


# from core urls: api/v1/service_providers/

app_name = "serivce_providers"

# router = DefaultRouter()
# router.register("", views.CRUDServiceProviders, basename='providers_crud') # Tareq

urlpatterns = [
    path('profile/update_data/', views.ServiceProviderUpdateRequestCreateAPI.as_view(), ),
    path('profile/approve_request/<int:pk>/', views.ServiceProviderApproveAPI.as_view()),
    
    # list locations - for everybody
    path("locations/<int:pk>/", maamoun_view.show_provider_locations, name="show_provider_locations"),
    path("locations/", maamoun_view.show_providers_locations, name="show_providers_locations"),
    
    # create location - authorized only
    path("locations/create/", maamoun_view.CreateLocation.as_view(), name="create_location"),
    path("location/<int:pk>/", maamoun_view.LocationRUD.as_view(), name="location_rud"),
    
    # path('location', Location.as_view()),
    # path('distance', ServiceProviderDistanceListView.as_view())
]

# urlpatterns += router.urls

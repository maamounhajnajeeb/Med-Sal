from rest_framework.routers import DefaultRouter

from django.urls import path

from service_providers import views, maamoun_view


# from core urls: api/v1/service_providers/

app_name = "serivce_providers"

router = DefaultRouter()
router.register("update_request", views.ServiceProviderUpdateRequestViewSet, basename='update_requests_crud')


urlpatterns = [
    # service provider checking update status
    path("check/", views.check_provider_update_status, name="check_provider_update_status"), #
    
    # list locations - for everybody
    path("locations/category/<int:pk>/", maamoun_view.show_category_locations, name="show_provider_locations"),
    path("locations/<int:pk>/", maamoun_view.show_provider_locations, name="show_provider_locations"),
    path("category/<int:pk>/", maamoun_view.show_category_providers, name="show_category_providers"),
    
    path("locations/", maamoun_view.show_providers_locations, name="show_providers_locations"),
    
    # create location - authorized only
    path("locations/create/", maamoun_view.CreateLocation.as_view(), name="create_location"),
    
    # Read, Delete, Update Specific location - safe method everybody - hard methods authorized only
    path("location/<int:pk>/", maamoun_view.LocationRUD.as_view(), name="location_rud"),
]

urlpatterns += router.urls

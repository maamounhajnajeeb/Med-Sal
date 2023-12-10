from rest_framework import routers

from django.urls import re_path, path

from services.views import maamoun_views, tareq_views, rates_views

router = routers.SimpleRouter()
router.register("rates", rates_views.ServiceRatesViewSet, basename="service_rates")

app_name = "services"

urlpatterns = [
    # create service
    path("create/", maamoun_views.CreateService.as_view(), name="create_service"),
    
    # rud services
    path("<int:pk>/", maamoun_views.ServiceRUD.as_view(), name="service_rud"),
    
    # all services
    path("", maamoun_views.ListAllServices.as_view(), name="all_services"),
    
    # category services
    # path("category/<int:category_id>/", maamoun_views.category_services, name="category_services"),
    
    # category services by name
    path("<str:category_name>/"
        , maamoun_views.category_services_by_name
        , name="category_services_by_name"),
    
    # provider services
    re_path(r"^provider/(\d{1,})?$", maamoun_views.provider_services, name="provider_services"),
    
    # location services
    path("location/<int:location_id>/", maamoun_views.provider_location_services, name="location_services"),
    
    # user rates
    re_path(r"^rates/user/(\d{1,})?$", rates_views.user_rates, name="user_rates"),
    
    # provider rates
    re_path(r"^rates/provider/(\d{1,})?$", rates_views.provider_rates, name="provider_rates"),
    
    # location rates
    path("rates/location/<int:location_id>/", rates_views.location_rates, name="location_rates"),
    
    # services categories
    path("categories/<int:provider_id>/", maamoun_views.provider_services_by_category, name="provider_services_by_category"),
    
    # provider categories services
    path("<int:provider_id>/<int:category_id>/", maamoun_views.provider_category_services, name="provider_category_services"),
    
    # list services by name
    path("servicename/", tareq_views.service_filter_by_name, name="service_by_name"),
    
    # list services by provider location (pk is provider_id)
    path("location/<int:pk>/", tareq_views.services_by_location, name="service_by_location"),
    
    # list services by distance
    path("distance/", tareq_views.services_by_distance, name="service_by_distance"),
    
    # list services in a category pk is (pk is category_id)
    path("category/<int:pk>/", tareq_views.services_by_category, name="service_for_category"),
]

urlpatterns += router.urls
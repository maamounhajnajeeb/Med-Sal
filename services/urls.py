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
    path("category/<int:category_id>/", maamoun_views.category_services, name="category_services"),
    
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
    
    # services categories
    path("<int:provider_id>/<int:category_id>/", maamoun_views.provider_category_services, name="provider_category_services"),
]

urlpatterns += router.urls
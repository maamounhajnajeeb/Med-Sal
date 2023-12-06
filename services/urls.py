from django.urls import re_path, path

from services.views import maamoun_views, tareq_views

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
    path("location/<int:location_id>/", maamoun_views.provider_location_services, name="location_services")
]

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
]

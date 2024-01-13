from django.urls import path

from . import views


app_name = "contact_us"

urlpatterns = [
    # create for everybody
    path("create/", views.CreateContcatUs.as_view(), name="create_contact_us"),
    
    # 
]

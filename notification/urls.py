from django.urls import re_path, path

from . import views

app_name = "notification"


urlpatterns = [
    
    path("provider/", views.provider_notifications, name="provider_notifications"),
    
    path("user/", views.user_notifications, name="user_notifications"),
    
    path("admin/", views.admin_notifications, name="admin_notifications"),
    
]

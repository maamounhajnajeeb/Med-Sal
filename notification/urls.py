from django.urls import path

from . import views

app_name = "notification"


urlpatterns = [
    # filter notifications for multiple user types
    path("<str:user_type>/", views.provider_notifications, name="provider_notifications"),
    
    # RUD Notification
    path("<int:pk>/", views.RUDNotification.as_view(), name="notification_rud_funcitonality"),
    
    # all notification (for admins only)
    path("all/", views.all_notification, name="all_notification"),
]

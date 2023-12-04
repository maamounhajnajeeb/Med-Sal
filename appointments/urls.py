from django.urls import re_path, path

from appointments.views import appointments_views, rejected_views

app_name = "appointments"


urlpatterns = [
    # appointments
    path("create/", appointments_views.CreateAppointment.as_view(), name="create_appointment"),
    
    path("<int:pk>/", appointments_views.AppointmentRUD.as_view(), name="rud-appointment"),
    
    re_path(r"provider/(\d{1,})?", appointments_views.provider_appointments, name="provider_appointments"),
    
    path("location/<int:location_id>/", appointments_views.location_appointments, name="location_appointments"),
    
    re_path(r"user/(\d{1,})?", appointments_views.user_appointments, name="user_appointments"),
    
]

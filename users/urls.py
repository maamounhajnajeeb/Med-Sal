from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("hello/", views.hello, name="hello"),
]

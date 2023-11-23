from django.urls import path

from .views import maamoun_views

app_name = "products"

urlpatterns = [
    path("", maamoun_views.CreateProduct.as_view(), name="create_product"),
]

from django.urls import path

from .views import maamoun_views, tareq_views

app_name = "products"

urlpatterns = [
    path("", maamoun_views.CreateProduct.as_view(), name="create_product"),
    
    path("category/<int:pk>", tareq_views.show_products_category, name="show_product_category"),

    
]

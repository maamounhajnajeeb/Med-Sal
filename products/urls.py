from django.urls import path

from .views import maamoun_views

app_name = "products"

urlpatterns = [
    # create product
    path("", maamoun_views.CreateProduct.as_view(), name="create_product"),
    
    # read, update, destroy specific product
    path("<int:pk>/", maamoun_views.RUDProduct.as_view(), name="specifc_product"),
    
    # view specific category products
    path("category/<int:pk>/", maamoun_views.products_by_category, name="products_by_category"),
    
    # view specific location products
    path("location/<int:pk>/", maamoun_views.products_by_location, name="products_by_location"),
    
    # view specific provider products
    path("service_provider/<int:pk>/", maamoun_views.products_by_provider, name="products_by_provider"),
    
    # view all products
    path("all/", maamoun_views.AllProducts.as_view(), name="all_products"),
]

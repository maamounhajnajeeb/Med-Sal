from rest_framework import routers

from django.urls import path, re_path

from .views import maamoun_views, rates_view, tareq_views

app_name = "products"


router = routers.SimpleRouter()
router.register("view/rates", rates_view.RatesViewSet, basename="rates_view") #


urlpatterns = [
    # all products rates (for admins only) #
    path("rates/all/", rates_view.all_products_rates, name="all_products_rates"),
    
    # create rate #
    path("rates/create/", rates_view.CreateRate.as_view(), name="create_rate"),
    
    # create product 
    path("", maamoun_views.CreateProduct.as_view(), name="create_product"),
    
    # read, update, destroy specific product #
    path("<int:pk>/", maamoun_views.RUDProduct.as_view(), name="specifc_product"),
    
    # activation switcher #
    path("<int:pk>/activation_switcher/", maamoun_views.activation_switcher, name="activation_switcher"),
    
    # search product #
    path("provider/search/<int:provider_id>/",
        maamoun_views.search_in_provider_products, name="search_in_provider_products"),
    
    # provider products stats
    # path("provider/stats/<int:provider_id>/", maamoun_views.provider_products_statistics, name="provider_products_statistics"),
    
    # view specific category products #
    path("category/<int:pk>/", maamoun_views.products_by_category, name="products_by_category"),
    
    # view specific location products #
    path("location/<int:pk>/", maamoun_views.products_by_location, name="products_by_location"),
    
    # view specific provider products #
    path("service_provider/<int:pk>/", maamoun_views.products_by_provider, name="products_by_provider"),
    
    # view all products #
    path("all/", maamoun_views.AllProducts.as_view(), name="all_products"),
    
    # view all products within price range #
    path("filter/price_range/", maamoun_views.products_price_range, name="products_price_range"),
    
    # user rates #
    re_path(r"^user/rates/(\d{1,})?$", rates_view.user_rates, name="user_rates"),
    
    # provider rates #
    re_path(r"^provider/rates/(\d{1,})?$", rates_view.provider_rates, name="provider_rates"),
    
    # product rates #
    path("<int:product_id>/rates/", rates_view.product_rates, name="product_rates"),
    
    # view products by distance #
    path("distance/", tareq_views.products_by_distance, name="products_by_distance"),
    
    # view products by name #
    path("product_name/", tareq_views.product_filter_by_name, name="products_by_name"),
    
    # view products by category name #
    path("<str:category_name>/", maamoun_views.category_products_by_name, name="category_products_by_name"),
]

urlpatterns += router.urls

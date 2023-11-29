from rest_framework.routers import SimpleRouter

from django.urls import path, re_path

from .views import maamoun_views, tareq_views, cart_views, orders_views


router = SimpleRouter()
router.register("cart", cart_views.CartViewSet, basename="cart_functionality")
router.register("", orders_views.OrderViewSet, basename="order_functionality")

app_name = "orders"

urlpatterns = [
    # user orders with it's items (you can put the user id, or via authenticated id)
    re_path(r"^user/(\d{1,})?$", orders_views.user_orders, name="user_orders"),
    
    # specifc item
    path("item/<int:pk>/", orders_views.ReadUpdateDestroyItem.as_view(), name="specific_item"),
    
    # user items
    re_path(r"^items/user/(\d{1,})?$", orders_views.user_items, name="user_items"),
    
    # all items
    path("items/all/", orders_views.all_items, name="all_items"),
    
    # filter items by status
    path("items/<str:stat>/", orders_views.filter_items, name="filter_items_by_status"),
    
    # provider items
    re_path(r"^provider/items/(\d{1,})?", orders_views.provider_items, name="provider_items"),
    
    # location items
    re_path(r"^location/items/(\d{1,})?", orders_views.location_items, name="location_items"),
    
    # user cart
    path("user/cart/", cart_views.user_cart, name="user_cart"),
    
    # 
    # path("", maamoun_views.CreateOrder.as_view(), name="create_list_orders"),
    
    # path("all/", maamoun_views.ListAllOrders.as_view(), name="all_orders"),
    
    # path("locations/<int:pk>/", maamoun_views.LocationOrders.as_view(), name="location_orders"),
    
    # path("providers/<int:pk>/", maamoun_views.ServiceProviderOrders.as_view(), name="provider_orders"),
    
]

urlpatterns += router.urls

from django.urls import path, re_path
from rest_framework import routers

from orders.views import cart_views, tareq_views, orders_views, rejected_orders_views


router = routers.SimpleRouter()

router.register("cart", cart_views.CartView, basename="cart")

app_name = "orders"

urlpatterns = [
    path("cart/user/", cart_views.user_cart, name="user_cart"),
    
    
]

urlpatterns += router.urls
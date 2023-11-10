from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.conf import settings

from . import views


urlpatterns = [
    
    # admin app
    path('admin/', admin.site.urls),
    
    # change language api
    path("api/v1/change_lang/", views.change_language, name="change_lang"),
    
    # users app
    path('api/v1/users/', include("users.urls", namespace="users")),
    
    # rest framework default [login, logout]
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework_auth')),
    
    # delivery app
    path("api/v1/delivery/", include("deliveries.urls", namespace="delivery")),
    
    # products app
    path("api/v1/products/", include("products.urls", namespace="products")),
    
    # orders app
    path("api/v1/orders/", include("orders.urls", namespace="orders")),
    
    # service_providers app
    path('api/v1/service_providers/', include("service_providers.urls", namespace="serivce_providers")),
    
    # category app
    path("api/v1/category/", include("category.urls", namespace="category")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

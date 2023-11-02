from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    
    # admin app
    path('admin/', admin.site.urls),
    
    # users app
    path('api/v1/', include("users.urls", namespace="users")),
    
    # rest framework default [login, logout]
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework_auth')),
    
    # delivery app
    path("api/v1/delivery/", include("deliveries.urls", namespace="delivery")),
    
    # products app
    path("api/v1/products/", include("products.urls", namespace="products")),
    
    # orders app
    path("api/v1/orders/", include("orders.urls", namespace="orders")),
    
    # service_providers app
    path('service_providers/', include("service_providers.urls", namespace="service_prov")),

    # for languages
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# category app [including language]
urlpatterns += i18n_patterns(
        path("api/v1/", include("category.urls", namespace="category")) )

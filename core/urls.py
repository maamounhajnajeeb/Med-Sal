from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.conf import settings

from . import views

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),)


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
    
    # permissions app
    path("api/v1/", include("permissions.urls", namespace="permissions")),
    
    # services app
    path("api/v1/services/", include("services.urls", namespace="services")),
    
    # notification app
    path("api/v1/notifications/", include("notification.urls", namespace="notification")),
    
    # appointments app
    path("api/v1/appointments/", include("appointments.urls", namespace="appointments")),
    
    # api document
    # path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

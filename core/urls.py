from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('api/v1/users/', include("users.urls", namespace="users")),
    path('api/v1/category/', include("category.urls", namespace="category")),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('api/v1/service_providers/', include("service_providers.urls", namespace="service_prov")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


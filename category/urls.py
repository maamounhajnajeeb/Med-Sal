from rest_framework import routers

from . import views

app_name = "category"

router = routers.SimpleRouter()
router.register("category", views.CRUDCategory, basename="category-functionality")

urlpatterns = [
    
]

urlpatterns += router.urls

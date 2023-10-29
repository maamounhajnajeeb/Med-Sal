from rest_framework import routers

from . import views

app_name = "category"

router = routers.SimpleRouter()
router.register("", views.CRUDCategory, basename="category-functionality")

url_patterns = [
    
]

url_patterns += router.urls
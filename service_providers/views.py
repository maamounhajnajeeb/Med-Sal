from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework import decorators

from django.db.models.functions import TruncMonth
from django.db.models import QuerySet, Count

from .models import UpdateProfileRequests
from . import permissions, serializers

from service_providers.models import ServiceProvider
from appointments.models import Appointments
from orders.models import OrderItem
from services.models import Service
from products.models import Product

from notification.models import Notification
from utils.permission import authorization_with_method



@decorators.api_view(["GET", ])
def check_provider_update_status(request: Request):
    provider_id: int = request.user.id
    queryset = UpdateProfileRequests.objects.filter(provider_requested=provider_id)
    if not queryset.exists():
        return Response({
            "message": "there is no such record for this provider"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.ServiceProviderUpdateRequestSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceProviderUpdateRequestViewSet(viewsets.ModelViewSet):
    queryset = UpdateProfileRequests.objects
    serializer_class = serializers.ServiceProviderUpdateRequestSerializer
    permission_classes = (permissions.UpdateRequestsPermission, )
    
    def create(self, request: Request, *args, **kwargs):
        service_provider, data = request.user.service_provider.id, request.data.copy()
        data["provider_requested"] = service_provider
        
        first_notf = {
            "sender": "System", "sender_type": "System"
            , "receiver": request.user.email, "receiver_type":"Service_Provider"
            , "ar_content": "تعديل الملف الشخصي بانتظار المراجعة"
            , "en_content": "Profile information editing is under revision"}
        
        second_notf = {
            "sender": "System", "sender_type": "System"
            , "receiver": "System", "receiver_type":"System"
            , "ar_content": "تعديل لملف شخصي بانتظار المراجعة"
            , "en_content": "Profile information editing is need revision"}
        
        Notification.objects.bulk_create([Notification(**first_notf), Notification(**second_notf)])
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        request.data["checked_by"] = request.user.id
        return super().update(request, *args, **kwargs)


def main_counter(provider_id: int, language: str):
    # stats
    stats = {}
    services_stats = Appointments.objects.filter(
        service__provider_location__service_provider=provider_id, status="accepted").values(
            f"service__{language}_title").annotate(
                count=Count("service"))
    services_stats = [
        {"title": stat[f"service__{language}_title"],"count": stat["count"]} for stat in services_stats
        ]
    
    products_stats = OrderItem.objects.filter(
        product__service_provider_location__service_provider=provider_id, status="ACCEPTED").values(
            f"product__{language}_title").annotate(
                count=Count("product"))
    products_stats = [
        {"title": stat[f"product__{language}_title"],"count": stat["count"]} for stat in products_stats
        ]
    
    user_stats = Appointments.objects.filter(
        service__provider_location__service_provider=30,
        result__isnull=False, status="accepted").values("result").annotate(count=Count("result"))
    user_stats = [
        {"result": stat["result"], "count": stat["count"]} for stat in user_stats
    ]
    
    stats["products_stats"], stats["services_stats"] = products_stats, services_stats
    stats["user_stats"] = user_stats
    
    # counts
    counts = {}
    services_count = Service.objects.filter(provider_location__service_provider=30).count()
    products_count = Product.objects.filter(service_provider_location__service_provider=30).count()
    users_count = Appointments.objects.filter(
        service__provider_location__service_provider=30, status="accepted").distinct("user").count()
    
    counts["product"], counts["services"], counts["users"] = services_count, products_count, users_count
    
    return counts, stats


@decorators.api_view(["GET", ])
@authorization_with_method("list", "appointments")
def provider_reports(req: Request):
    language = req.META.get("Accept-Language")
    counts, stats = main_counter(req.user.id, language)
    
    products_diagram = Product.objects.filter(
        service_provider_location__service_provider=30).annotate(
            month=TruncMonth("updated_at")).values("month").annotate(products=Count("id"))
    products_diagram = [
        {"year": result["month"].year, "month": result["month"].month, "products_count": result["products"]}
        for result in products_diagram
    ]
    
    services_diagram = Service.objects.filter(
        provider_location__service_provider=30).annotate(
            month=TruncMonth("updated_at")).values("month").annotate(
                services=Count("id"))
    services_diagram = [
        {"year": result["month"].year, "month": result["month"].month, "services_count": result["services"]}
        for result in services_diagram
    ]
    
    response = {
        "stats": stats,
        "counts": counts,
        "services_diagram": services_diagram,
        "products_diagram": products_diagram,
    }
    
    return Response(response, status=status.HTTP_200_OK)

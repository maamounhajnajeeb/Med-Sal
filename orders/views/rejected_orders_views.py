from rest_framework import viewsets, status
from rest_framework.response import Response


from orders import models, serializers

from utils.permission import HasPermission


class RejectedOrdersViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RejectedOrderSerializer
    queryset = models.RejectedOrders.objects
    permission_classes = (HasPermission, )
    
    def get_permissions(self):
        return [permission("rejectedorders") for permission in self.permission_classes]

from rest_framework import serializers

from django.db import models

from typing import Any

from . import models

from products.serializers import ProudctSerializer
from deliveries.models import Delivery



""" **{ the below two serializers used in CreateOrder view class }** """
class OrdersItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.OrderItem
        fields = ("product", "quantity", "price", "status",)

class OrdersSerializer(serializers.ModelSerializer):
    items = OrdersItemsSerializer(many=True)
    paid = serializers.BooleanField(default=False)
    delivered = serializers.BooleanField(default=False)
    
    class Meta:
        model = models.Orders
        fields = ("patient", "items", "paid", "delivered")
    
    def create(self, validated_data: dict[str, Any]):
        """
        first we create Order instance without price
        then we make a list of order items
        we use bulk create to create (one or more) OrderItmes objects related with the previous order instance
        then we change the Order instance price with the sum of all OrderItems objects prices
        and we return the Order instance
        """
        patient_obj = validated_data.pop("patient")
        order = models.Orders.objects.create(patient=patient_obj)
        
        paid = validated_data.pop("paid")
        delivery_obj = Delivery.objects.create(order=order, paid=paid)
        
        OrdersItems = []
        for OrderDict in validated_data.get("items"):
            product, quantity = OrderDict["product"], OrderDict["quantity"] or 1
            price = OrderDict["price"]
            
            item = models.OrderItem(order=order, product=product, quantity=quantity, price=price)
            OrdersItems.append(item)
        
        models.OrderItem.objects.bulk_create(OrdersItems)
        
        return order
    
    def update(self, instance: models.Orders, validated_data):
        if validated_data.get("paid") is not None:
            delivery_obj = instance.delivery
            delivery_obj.paid = validated_data.pop("paid")
            delivery_obj.save()
        
        if validated_data.get("delivered") is not None:
            delivery_obj = instance.delivery
            delivery_obj.delivered = validated_data.pop("delivered")
            delivery_obj.save()
        
        return super().update(instance, validated_data)
    
    def to_representation(self, instance: models.Orders):
        items_queryset = instance.items.all()
        items_serializer = OrdersItemsSerializer(items_queryset, many=True)
        
        return {
            'order_id': instance.id,
            'patient_id': instance.patient.id,
            'patient_email': str(instance.patient),
            'paid': instance.delivery.paid,
            'delivered': instance.delivery.delivered,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at or "No Update on this order",
            'products': items_serializer.data
        }


""" **{ the below serializer used in ReadUpdateDeleteItem view class }** """
class ItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = "__all__"
        model = models.OrderItem
    
    def update(self, instance: models.OrderItem, validated_data: dict[str, Any]):
        if validated_data.get("status"):
            if validated_data.get("status") == "ACCEPTED":
                product = instance.product
                product.quantity -= instance.quantity
                product.save()
                
            if validated_data.get("status") == "REJECTED":
                # here we will work with rejected orders
                print("refuse")
        return super().update(instance, validated_data)


""" **{ the below two serializers used in ListAllOrders view }** """
class ListOrderItemSer(serializers.ModelSerializer):
    product = ProudctSerializer(read_only=True)
    
    class Meta:
        fields = ("quantity", "product", )
        model = models.OrderItem

class ListOrderSer(serializers.ModelSerializer):
    items = ListOrderItemSer(many=True, read_only=True)
    
    class Meta:
        fields = ("patient", "status", "created_at", "updated_at", "items", )
        model = models.Orders
    
    def __init__(self, instance=None, data=..., **kwargs):
        self.language = kwargs.pop("fields")["language"]
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance):
        return {
            "patient_id": instance.patient.id
            , "patient_email": instance.patient.email
            , "status": instance.status
            , "created_at": instance.created_at
            , "upated_at": instance.updated_at
            , "products": [
                {
                    "quantity": item.quantity,
                "product_name": item.product.ar_title if self.language == "ar" else item.product.en_title
                }
                for item in instance.items.all()
                ]
        }


""" **{ the below serializer used in LocationOrders view }** """
class LocationOrdersSer(serializers.ModelSerializer):
    product = ProudctSerializer(read_only=True)
    
    class Meta:
        fields = ("quantity", "product", "price", )
        model = models.OrderItem
    
    def __init__(self, instance=None, data=..., **kwargs):
        self.language = kwargs.pop("fields")["language"]
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance):
        
        show_date_time = lambda x: f"{x.month}/{x.day}/{x.year} at {x.hour}:{x.minute}:{x.second}"
        
        product = instance.product
        return {
            "quantity": instance.quantity
            , "product_name": product.ar_title if self.language == "ar" else product.en_title
            , "price": instance.price
            , "status": instance.order.status
            , "created_at": show_date_time(instance.order.created_at)
            , "updated_at": show_date_time(instance.order.updated_at)
        }


""" **{ serializer below user in cart views classes and functions}** """
class CartSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.CartItems
        fields = ("id", "product", "quantity", "patient", )
    
    def __init__(self, instance=None, data=..., **kwargs):
        additional_fields = kwargs.get("fields")
        if additional_fields:
            additional_fields = kwargs.pop("fields")
            self.language = additional_fields.get("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance):
        return {
            "cart_id": instance.id
            , "patient_id": instance.patient.id
            , "product_id": instance.product.id
            , "product_name": instance.product.ar_title if self.language == "ar" else instance.product.en_title
            , "quantity": instance.quantity
            }

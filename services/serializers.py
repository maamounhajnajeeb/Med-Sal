from rest_framework import serializers

from .helpers import FileMixin

from . import models


class CreateServicesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Service
        fields = "__all__"
    
    def to_representation(self, instance: models.Service):
        return {
            "id": instance.id
            , "provider_location_id": instance.provider_location.id
            , "provider_name": instance.provider_location.service_provider.business_name
            , "category_name": instance.category.en_name
            , "ar_title": instance.ar_title
            , "en_title": instance.en_title
            , "ar_description": instance.ar_description
            , "en_description": instance.en_description
            , "images": instance.image.split(",")
            , "price": instance.price
            , "created_at": instance.created_at
            , "updated_at": instance.updated_at
        }


class RUDServicesSerializer(serializers.ModelSerializer, FileMixin):
    
    class Meta:
        model = models.Service
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if not language:
            self.language = language
        else:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def update(self, instance, validated_data):
        images_paths = instance.image
        self.delete_images(images_paths)
        return super().update(instance, validated_data)
    
    def to_representation(self, instance: models.Service):
        category = instance.category
        
        return {
            "id": instance.id
            , "provider_location_id": instance.provider_location.id
            , "provider_name": instance.provider_location.service_provider.business_name
            , "category_name": category.en_name if self.language == "en" else category.ar_name
            , "title": instance.ar_title if self.language == "ar" else instance.en_title
            , "description": instance.ar_description if self.language == "ar" else instance.en_description
            , "images": instance.image.split(",")
            , "price": instance.price
            , "created_at": instance.created_at
            , "updated_at": instance.updated_at
        }
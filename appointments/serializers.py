from rest_framework import serializers

from .models import AppointmentsDraft


class DraftSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = AppointmentsDraft
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if not language:
            self.language = None
        else:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance: AppointmentsDraft):
        return {
            "provider": instance.service.provider_location.service_provider.email
            , "service": instance.service.ar_title if self.language == "ar" else instance.service.en_title
            , "user": instance.user.email
            , "from_time": instance.from_time
            , "to_time": instance.to_time
            , "date": instance.date
            , "created_at": instance.created_at
            , "updated_at": instance.updated_at
        }

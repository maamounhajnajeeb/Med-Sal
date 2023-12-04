from rest_framework import serializers

from .models import Appointments, RejectedAppointments


# class DraftSerializers(serializers.ModelSerializer):
    
#     class Meta:
#         model = AppointmentsDraft
#         fields = "__all__"
    
#     def __init__(self, instance=None, data=..., **kwargs):
#         language = kwargs.get("language")
#         if not language:
#             self.language = None
#         else:
#             self.language = kwargs.pop("language")
        
#         super().__init__(instance, data, **kwargs)
    
#     def to_representation(self, instance: AppointmentsDraft):
#         return {
#             "id": instance.id
#             , "provider": instance.service.provider_location.service_provider.email
#             , "provider_location_id": instance.service.provider_location.id
#             , "service": instance.service.ar_title if self.language == "ar" else instance.service.en_title
#             , "service_id": instance.service.id
#             , "user": instance.user.email
#             , "user_id": instance.user.id
#             , "from_time": instance.from_time
#             , "to_time": instance.to_time
#             , "date": instance.date
#             , "created_at": instance.created_at
#             , "updated_at": instance.updated_at
#         }


class AppointmentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Appointments
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if not language:
            self.language = None
        else:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance: Appointments):
        original_repr =  super().to_representation(instance)
        original_repr["user_email"] = instance.user.email
        original_repr["service_title"] = instance.service.ar_title if self.language == "ar" else instance.service.en_title
        original_repr["location_id"] = instance.service.provider_location.id
        
        return original_repr


class ShowAppointmentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Appointments
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if not language:
            self.language = None
        else:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance: Appointments):
        return {
            "date": instance.date
            , "details": {
                "user_id": instance.user.id
                , "user_email": instance.user.email
                , "service_id": instance.service.id
                , "service_title": instance.service.en_title if self.language == "en" else instance.service.ar_title
                , "provider_id": instance.service.provider_location.service_provider.id
                , "provider_name": instance.service.provider_location.service_provider.business_name
                , "location_id": instance.service.provider_location.id
                , "created_at": instance.created_at
            }
        }

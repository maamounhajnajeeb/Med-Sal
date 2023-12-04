from rest_framework import status, decorators
from rest_framework.response import Response
from rest_framework import generics

from django.http import HttpRequest

from typing import Optional

from appointments import models, serializers



class CreateAppointment(generics.CreateAPIView):
	queryset = models.Appointments.objects
	serializer_class = serializers.AppointmentsSerializer
	
	def create(self, request: HttpRequest, *args, **kwargs):
		language = request.META.get("Accept-Language")
		
		serializer = self.get_serializer(data=request.data, language=language)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AppointmentRUD(generics.RetrieveUpdateDestroyAPIView):
	queryset = models.Appointments.objects
	serializer_class = serializers.AppointmentsSerializer
	
	def get_serializer(self, *args, **kwargs):
		language = self.request.META.get("Accept-Language")
		kwargs.setdefault("language", language)
		
		serializer_class = self.get_serializer_class()
		kwargs.setdefault('context', self.get_serializer_context())
		return serializer_class(*args, **kwargs)
	
	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.get_serializer([instance, ], many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def location_appointments(request: HttpRequest, location_id: int):
    language = request.META.get("Accept-Language")
    queryset = models.Appointments.objects.filter(service__provider_location=location_id)
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def provider_appointments(request: HttpRequest, provider_id: Optional[int]):
    language = request.META.get("Accept-Language")
    provider_id = provider_id or request.user.id
    queryset = models.Appointments.objects.filter(service__provider_location__service_provider=provider_id)
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def user_appointments(request: HttpRequest, user_id: Optional[int]):
    language = request.META.get("Accept-Language")
    user_id = user_id or request.user.id
    
    queryset = models.Appointments.objects.filter(user__id=user_id)
    serializer = serializers.ShowAppointmentsSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

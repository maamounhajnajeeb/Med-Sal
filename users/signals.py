# from django.dispatch import receiver
# from djoser.signals import user_registered
# from rest_framework import serializers

# @receiver(user_registered)
# def add_two_factor_enabled_to_serializer(sender, request, user, **kwargs):
#     user_serializer = sender.get('user')
#     user_serializer.fields['two_factor_enabled'] = serializers.BooleanField(required=False)

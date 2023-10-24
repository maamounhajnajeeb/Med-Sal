from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(pre_save, sender=User)
def my_callback(sender, instance: User, *args, **kwargs):
    pwd = instance.password
    instance.set_password(pwd)

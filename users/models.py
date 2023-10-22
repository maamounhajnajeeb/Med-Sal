from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.query import QuerySet

# Create your models here.
class CustomUsers(AbstractUser):
    
    class Types(models.TextChoices):
        SERVICE_PROVIDER = ("SERVICE_PROVIDER", "Service_Provider")
        ADMIN = ("ADMIN", "Admin")
        USER = ("USER", "User")
    
    base_type = Types.USER
    
    type = models.CharField("Type", max_length=50, choices=Types.choices, default=Types.USER)
    
    def __str__(self) -> str:
        return self.username


class ServiceProvider(CustomUsers):
    
    isbn = models.IntegerField()


class AdminsManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        result = super().get_queryset()
        return result.filter(type=CustomUsers.Types.ADMIN)


class Admins(CustomUsers):
    
    base_type = CustomUsers.Types.ADMIN
    
    objects = AdminsManager()
    
    class Meta:
        proxy = True


# class ProvidersManager(models.Manager):
#     def get_queryset(self) -> QuerySet:
#         result = super().get_queryset()
#         return result.filter(type=CustomUsers.Types.SERVICE_PROVIDER)


# class ServiceProviderProxy(CustomUsers):
    
#     base_type = CustomUsers.Types.SERVICE_PROVIDER
    
#     objects = ProvidersManager()
    
#     class Meta:
#         proxy = True


# class ServiceProvider(ServiceProviderProxy):
#     isbn_number = models.IntegerField()
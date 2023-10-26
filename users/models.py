from collections.abc import Iterable
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.query import QuerySet

class Users(AbstractUser):
    
    class Types(models.TextChoices):
        SERVICE_PROVIDER = ("SERVICE_PROVIDER", "Service_Provider")
        SUPER_ADMIN = ("SUPER_ADMIN", "Super_Admin")
        ADMIN = ("ADMIN", "Admin")
        USER = ("USER", "User")
    
    email = models.EmailField(max_length=128, unique=True, null=False)
    image = models.ImageField(upload_to="profile_images/", default="defaults/default_profile.jpg")
    
    base_type = Types.USER
    user_type = models.CharField(max_length=32, choices=Types.choices, default=base_type)
    
    REQUIRED_FIELDS = []
    
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    
    class Meta:
        verbose_name = "Users"
    
    def __str__(self) -> str:
        return self.username


class SuperAdminsManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        result = super().get_queryset()
        return result.filter(user_type=Users.Types.SUPER_ADMIN)

class SuperAdmins(Users):
    base_type = Users.Types.SUPER_ADMIN
    
    admins = SuperAdminsManager()
    
    is_staff = True
    is_superuser = True

    class Meta:
        proxy = True
        verbose_name = "SuperAdmins"


class AdminsManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        result = super().get_queryset()
        return result.filter(user_type=Users.Types.ADMIN)

class Admins(Users):
    base_type = Users.Types.SUPER_ADMIN
    
    is_staff = True
    admins = AdminsManager()
    
    class Meta:
        proxy = True
        verbose_name = "Admins"

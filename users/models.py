from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models.query import QuerySet

class CusotmManager(UserManager):
    def create_user(self, username: str, email: str | None = ..., password: str | None = ..., **extra_fields):
        is_staff, is_superuser = extra_fields.get("is_staff"), extra_fields.get("is_superuser")
        print(is_superuser)
        if not is_staff:
            extra_fields.setdefault("is_staff", False)
        if not is_superuser:
            extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

class Users(AbstractUser):
    
    class Types(models.TextChoices):
        SERVICE_PROVIDER = ("SERVICE_PROVIDER", "Service_Provider")
        SUPER_ADMIN = ("SUPER_ADMIN", "Super_Admin")
        ADMIN = ("ADMIN", "Admin")
        USER = ("USER", "User")
    
    username = models.CharField(max_length=128, unique=False)
    email = models.EmailField(max_length=128, unique=True, null=False)
    image = models.ImageField(upload_to="profile_images/", default="defaults/default_profile.jpg")
    
    base_type = Types.USER
    user_type = models.CharField(max_length=32, choices=Types.choices, default=base_type)
    
    objects = CusotmManager()
    
    REQUIRED_FIELDS = []
    
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    
    class Meta:
        verbose_name = "Users"
    
    def __str__(self) -> str:
        return self.email


class SuperAdminsManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        result = super().get_queryset()
        return result.filter(user_type=Users.Types.SUPER_ADMIN)

class SuperAdmins(Users):
    base_type = Users.Types.SUPER_ADMIN
    
    AbstractUser.is_superuser = True
    AbstractUser.is_staff = True
    
    admins = SuperAdminsManager()
    
    class Meta:
        proxy = True
        verbose_name = "SuperAdmins"


class AdminsManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        result = super().get_queryset()
        return result.filter(user_type=Users.Types.ADMIN)

class Admins(Users):
    base_type = Users.Types.SUPER_ADMIN
    
    AbstractUser.is_staff = True
    
    admins = AdminsManager()
    
    class Meta:
        proxy = True
        verbose_name = "Admins"
    

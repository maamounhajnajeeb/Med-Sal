from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models.query import QuerySet

<<<<<<< HEAD
from . import utils
=======
from django.contrib.auth.models import (
    BaseUserManager,
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")

        return self.create_user(email, password, **extra_fields)

>>>>>>> 2fdb9f7c5f6430580c04aef87337da0a97069d11

class Users(AbstractUser):
    class Types(models.TextChoices):
        SERVICE_PROVIDER = ("SERVICE_PROVIDER", "Service_Provider")
        SUPER_ADMIN = ("SUPER_ADMIN", "Super_Admin")
        ADMIN = ("ADMIN", "Admin")
        USER = ("USER", "User")
<<<<<<< HEAD
    
    username = models.CharField(max_length=128, unique=False, null=True, blank=True)
    email = models.EmailField(max_length=128, unique=True, null=False)
    image = models.ImageField(
        upload_to=utils.unique_image_name, default="defaults/default_profile.jpg")
    
=======

    username = None
    email = models.EmailField(max_length=128, unique=True, null=False)
    image = models.ImageField(
        upload_to="profile_images/", default="defaults/default_profile.jpg"
    )

>>>>>>> 2fdb9f7c5f6430580c04aef87337da0a97069d11
    base_type = Types.USER
    user_type = models.CharField(
        max_length=32, choices=Types.choices, default=base_type
    )
    email_confirmed = models.BooleanField(default=False)
    # 2FA
    two_factor_enabled = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_generated_at = models.DateTimeField(blank=True, null=True)
    is_verification_email_sent = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["user_type"]

    USERNAME_FIELD = "email"
    # EMAIL_FIELD = "email"

    objects = CustomUserManager()

    class Meta:
<<<<<<< HEAD
        verbose_name = "User"
        verbose_name_plural = "User"
    
=======
        verbose_name = "Users"

>>>>>>> 2fdb9f7c5f6430580c04aef87337da0a97069d11
    def __str__(self) -> str:
        return str(self.email)

    def generate_verification_code(self):
        import random
        import string

        code = "".join(random.choice(string.digits) for _ in range(6))
        self.verification_code = code
        self.verification_code_generated_at = timezone.now()
        self.two_factor_enabled = True
        self.save()
        return code

    def verify_two_factor_code(self, code):
        # Verify the provided 2FA code
        current_time = timezone.now()
        if (
            self.verification_code
            and self.verification_code_generated_at
            and current_time - self.verification_code_generated_at
            <= timezone.timedelta(minutes=20)
            and code == self.verification_code
        ):
            self.clear_verification_code()
            self.is_verification_email_sent = True
            return True
        return False

    def clear_verification_code(self):
        self.verification_code = None
        self.verification_code_generated_at = None
        self.save()

    def enable_2fa(self):
        self.two_factor_enabled = True
        self.clear_verification_code()
        self.save()

    def disable_2fa(self):
        self.two_factor_enabled = False
        self.clear_verification_code()
        self.save()


class SuperAdminsManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        result = super().get_queryset()
        return result.filter(user_type=Users.Types.SUPER_ADMIN)


class SuperAdmins(Users):
    base_type = Users.Types.SUPER_ADMIN
<<<<<<< HEAD
    Users.user_type = models.CharField(max_length=32, choices=Users.Types.choices, default=base_type)
    
=======

>>>>>>> 2fdb9f7c5f6430580c04aef87337da0a97069d11
    super_admins = SuperAdminsManager()
    
    class Meta:
        proxy = True
        verbose_name = "SuperAdmin"
        verbose_name_plural = "SuperAdmin"


class AdminsManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        result = super().get_queryset()
        return result.filter(user_type=Users.Types.ADMIN)


class Admins(Users):
<<<<<<< HEAD
    base_type = Users.Types.ADMIN
    Users.user_type = models.CharField(max_length=32, choices=Users.Types.choices, default=base_type)
    
=======
    base_type = Users.Types.SUPER_ADMIN

>>>>>>> 2fdb9f7c5f6430580c04aef87337da0a97069d11
    admins = AdminsManager()

    class Meta:
        proxy = True
<<<<<<< HEAD
        verbose_name = "Admin"
        verbose_name_plural = "Admin"
        
=======
        verbose_name = "Admins"
>>>>>>> 2fdb9f7c5f6430580c04aef87337da0a97069d11

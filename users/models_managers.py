from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password

from typing import Any


class MyUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("Users must have an email address")
        
        user = self.model(
            email=self.normalize_email(email)
            , password=make_password(password)
            , **kwargs)
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)
        
        if kwargs.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(**kwargs)
    
    def get_by_natural_key(self, email: None) -> Any:
        email = self.normalize_email(email)
        return self.get(**{self.model.USERNAME_FIELD: email})

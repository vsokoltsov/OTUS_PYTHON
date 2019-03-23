from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)


class User(AbstractBaseUser):
    """Represents a user object in our system."""

    email = models.EmailField(max_length=255, unique=True, null=False)
    login = models.CharField(max_length=255, unique=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField()

    objects = BaseUserManager()

    USERNAME_FIELD = 'login'

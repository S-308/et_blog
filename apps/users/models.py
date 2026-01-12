from django.contrib.auth.models import AbstractUser, UserManager
from apps.core.base import ActiveUserManager, BaseModel
from django.db import models


class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True)

    objects = ActiveUserManager()
    all_objects = UserManager()   

    def __str__(self):
        return self.username

from django.db import models
from apps.core.base import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name

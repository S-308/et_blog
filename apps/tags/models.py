from django.db import models
from apps.users.models import BaseModel


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name

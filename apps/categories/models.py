from django.db import models, transaction
from django.utils import timezone
from apps.core.base import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ("id",)

    def soft_delete(self):
        """
        Soft delete this category only.
        Does NOT cascade to posts.
        """
        with transaction.atomic():
            if self.is_deleted:
                return

            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        """
        Restore this category only.
        """
        with transaction.atomic():
            if not self.is_deleted:
                return

            self.is_deleted = False
            self.deleted_at = None
            self.save(update_fields=["is_deleted", "deleted_at"])

    def __str__(self):
        return self.name

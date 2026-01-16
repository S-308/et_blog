from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, UserManager
from apps.core.base import ActiveUserManager, BaseModel


class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True)

    objects = ActiveUserManager()
    all_objects = UserManager()

    def soft_delete(self):
        """
        Soft Delete the user and mark as deleted.
        """
        with transaction.atomic():
            if self.is_deleted:
                return

            self.is_active = False
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=["is_active", "is_deleted", "deleted_at"])

    def restore(self):
        """
        Restore user account
        """
        with transaction.atomic():
            if not self.is_deleted:
                return

            self.is_deleted = False
            self.deleted_at = None
            self.save(update_fields=["is_deleted", "deleted_at"])

    def __str__(self):
        return self.username

from django.conf import settings
from django.db import models, transaction
from apps.posts.models import Post
from apps.core.base import BaseModel
from django.core.exceptions import ValidationError
from .constants import MAX_COMMENT_DEPTH
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Comment(BaseModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    content = models.TextField()

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies"
    )

    depth = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("id",)

    def clean(self):
        if self.parent:
            if self.parent.post_id != self.post_id:
                raise ValidationError(
                    {"parent": "Parent comment must belong to the same post."}
                )

            if self.parent.depth >= MAX_COMMENT_DEPTH:
                raise ValidationError(
                    {"parent": f"Max comment depth of {MAX_COMMENT_DEPTH} exceeded."}
                )

            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    def soft_delete(self):
        """
        Soft delete this comment only.
        """
        with transaction.atomic():
            if self.is_deleted:
                return

            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        """
        Restore this comment only.
        """
        with transaction.atomic():
            if not self.is_deleted:
                return

            if self.post.is_deleted:
                return  # or raise ValidationError

            self.is_deleted = False
            self.deleted_at = None
            self.save(update_fields=["is_deleted", "deleted_at"])

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Comment #{self.id} by {self.author}"

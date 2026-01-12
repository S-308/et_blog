from django.conf import settings
from django.db import models
from apps.posts.models import Post
from apps.users.models import BaseModel

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

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"Comment #{self.id} by {self.author}"

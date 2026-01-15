from django.contrib import admin
from .models import Comment

@admin.action(description="Restore selected comments")
def restore_comments(modeladmin, request, queryset):
    queryset.update(is_deleted=False, deleted_at=None)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display_links = ("post",)
    list_display = ("id", "post", "author", "created_at")
    list_filter = ("is_deleted",)
    ordering = ("id",)
    actions = [restore_comments]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            object_id = request.resolver_match.kwargs.get("object_id")

            if object_id:
                try:
                    comment = Comment.objects.get(pk=object_id)
                    kwargs["queryset"] = (
                        Comment.objects
                        .filter(post=comment.post, is_deleted=False)
                        .exclude(pk=comment.pk)
                    )

                except Comment.DoesNotExist:
                    pass

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        return Comment.all_objects.all()
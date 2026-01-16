from django.contrib import admin
from .models import Comment
from .constants import MAX_COMMENT_DEPTH

@admin.action(description="Soft Delete Selected Comments")
def soft_delete_comments(modeladmin, request, queryset):
    for comment in queryset:
        comment.soft_delete()

@admin.action(description="Restore Selected Comments")
def restore_comments(modeladmin, request, queryset):
    for comment in queryset:
        comment.restore()

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display_links = ("post",)
    list_display = ("id", "post", "author", "depth", "created_at")
    list_filter = ("is_deleted",)
    ordering = ("id",)
    actions = [soft_delete_comments, restore_comments]
    readonly_fields = ("depth",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            object_id = request.resolver_match.kwargs.get("object_id")

            if object_id:
                try:
                    comment = Comment.objects.get(pk=object_id)
                    kwargs["queryset"] = (
                        Comment.objects
                        .filter(
                            post=comment.post,
                            is_deleted=False,
                            depth__lt=MAX_COMMENT_DEPTH - 1
                        )
                        .exclude(pk=comment.pk)
                    )
                except Comment.DoesNotExist:
                    pass

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        return Comment.all_objects.all()

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None) 
        return actions

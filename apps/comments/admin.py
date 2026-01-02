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

    def get_queryset(self, request):
        return Comment.all_objects.all()
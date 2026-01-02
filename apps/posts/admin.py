from django.contrib import admin
from .models import Post

@admin.action(description="Restore selected posts")
def restore_posts(modeladmin, request, queryset):
    queryset.update(
        is_deleted=False,
        deleted_at=None,
    )

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display_links = ("title",)
    list_display = ("id", "title", "author", "status", "created_at")
    list_filter = ("status", "created_at","is_deleted")
    actions = [restore_posts]
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}

    def get_queryset(self, request):
        return Post.all_objects.all()

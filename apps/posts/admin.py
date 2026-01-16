from django.contrib import admin
from .models import Post

@admin.action(description="Soft delete selected posts")
def soft_delete_posts(modeladmin, request, queryset):
    for post in queryset:
        post.soft_delete()

@admin.action(description="Restore selected posts")
def restore_posts(modeladmin, request, queryset):
    for post in queryset:
        post.restore()


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display_links = ("title",)
    list_display = ("id", "title", "author", "status", "created_at")
    list_filter = ("status", "created_at","is_deleted")
    actions = [soft_delete_posts, restore_posts]
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}

    def get_queryset(self, request):
        return Post.all_objects.all()
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

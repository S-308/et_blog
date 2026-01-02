from django.contrib import admin
from .models import Tag

@admin.action(description="Restore selected tags")
def restore_tags(modeladmin, request, queryset):
    queryset.update(is_deleted=False, deleted_at=None)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display_links = ("name",)
    list_display = ("id", "name", "slug", "created_at")
    list_filter = ("is_deleted",)
    ordering = ("id",)
    prepopulated_fields = {"slug": ("name",)}
    actions = [restore_tags]

    def get_queryset(self, request):
        return Tag.all_objects.all()

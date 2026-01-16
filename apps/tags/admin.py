from django.contrib import admin
from .models import Tag


@admin.action(description="Soft Delete Selected Tags")
def soft_delete_tags(modeladmin, request, queryset):
    for tag in queryset:
        tag.soft_delete()


@admin.action(description="Restore Selected Tags")
def restore_tags(modeladmin, request, queryset):
    for tag in queryset:
        tag.restore()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display_links = ("name",)
    list_display = ("id", "name", "slug", "created_at", "is_deleted")
    list_filter = ("is_deleted",)
    ordering = ("id",)
    prepopulated_fields = {"slug": ("name",)}
    actions = [soft_delete_tags, restore_tags]

    def get_queryset(self, request):
        return Tag.all_objects.all()

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

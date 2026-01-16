from django.contrib import admin
from .models import Category


@admin.action(description="Soft delete selected categories")
def soft_delete_categories(modeladmin, request, queryset):
    for category in queryset:
        category.soft_delete()


@admin.action(description="Restore selected categories")
def restore_categories(modeladmin, request, queryset):
    for category in queryset:
        category.restore()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display_links = ("name",)
    list_display = ("id", "name", "slug", "created_at")
    list_filter = ("is_deleted",)
    ordering = ("id",)
    prepopulated_fields = {"slug": ("name",)}
    actions = [soft_delete_categories, restore_categories]

    def get_queryset(self, request):
        return Category.all_objects.all()

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

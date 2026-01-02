from django.contrib import admin
from .models import Category

@admin.action(description="Restore selected categories")
def restore_categories(modeladmin, request, queryset):
    queryset.update(is_deleted=False, deleted_at=None)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display_links = ("name",)
    list_display = ("id", "name", "slug", "created_at")
    list_filter = ("is_deleted",)
    ordering = ("id",)
    prepopulated_fields = {"slug": ("name",)}
    actions = [restore_categories]

    def get_queryset(self, request):
        return Category.all_objects.all()
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.action(description="Restore selected users")
def restore_users(modeladmin, request, queryset):
    queryset.update(
        is_deleted=False,
        deleted_at=None,
    )

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    ordering = ("id",)
    list_display_links = ("username",)
    list_display = ("id", "username", "email", "is_staff", "is_active", "created_at")
    list_filter = ("is_staff", "is_active","is_deleted")
    actions = [restore_users]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Audit Info", {"fields": ("created_at", "updated_at", "created_by", "updated_by")}),
    )

    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

    def get_queryset(self, request):
        return User.all_objects.all()

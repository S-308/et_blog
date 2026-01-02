from rest_framework.permissions import BasePermission

class IsAuthorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("GET",):
            return True

        if request.user.is_staff or request.user.is_superuser:
            return True

        return obj.author == request.user

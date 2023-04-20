from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorOrReadOnly(BasePermission):
    """Полный доступ автору, для остальных только чтение"""

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


class AdminOrReadOnly(BasePermission):
    """Полный доступ для администратора,
    для остальных только чтение"""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_staff
        )

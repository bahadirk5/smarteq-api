from rest_framework import permissions

class IsAdminOrRoles(permissions.BasePermission):
    """
    Sadece superuser veya belirtilen role sahip kullanıcılar erişebilir.
    allowed_roles: List[str]
    """
    allowed_roles = []

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (
                user.is_superuser or
                (hasattr(user, 'role') and user.role and user.role.name in self.allowed_roles)
            )
        )

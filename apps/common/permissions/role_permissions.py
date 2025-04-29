from rest_framework import permissions

class IsSuperUser(permissions.BasePermission):
    """
    Permission to only allow superusers.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

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

class IsSystemAdmin(IsAdminOrRoles):
    allowed_roles = ['Sistem Yöneticisi']

class IsSystemAdminOrSoftwareDeveloper(IsAdminOrRoles):
    allowed_roles = ['Sistem Yöneticisi', 'Yazılım Uzmanı']

class IsSoftwareDeveloper(permissions.BasePermission):
    """
    Permission to only allow software developers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.role and 
            request.user.role.name == 'Yazılım Uzmanı'
        )

class IsHardwareExpert(permissions.BasePermission):
    """
    Permission to only allow hardware experts.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.role and 
            request.user.role.name == 'Donanım Uzmanı'
        )

class IsTechnicalSupport(permissions.BasePermission):
    """
    Permission to only allow technical support staff.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.role and 
            request.user.role.name in ['Teknik Destek Uzmanı', 'Kıdemli Teknik Uzman']
        )

class IsDealerNetwork(permissions.BasePermission):
    """
    Permission to only allow dealer network staff.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.role and 
            request.user.role.name in [
                'Bayi Temsilcisi', 'Filo Yöneticisi', 
                'Kıdemli Filo Yöneticisi', 'Filo Yetkilisi'
            ]
        )

class IsInstitutionManager(permissions.BasePermission):
    """
    Permission to only allow institution managers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.role and 
            request.user.role.name in ['Kurum Yöneticisi', 'Kıdemli Kurum Yöneticisi']
        )

class IsAdvancedInstitutionManager(permissions.BasePermission):
    """
    Permission to only allow senior institution managers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.role and 
            request.user.role.name == 'Kıdemli Kurum Yöneticisi'
        )
class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow only owners of objects or admins to perform actions on them.
    """
    def has_object_permission(self, request, view, obj):
        # Admin level roles have full access
        if request.user.is_superuser or (
            request.user.role and 
            request.user.role.name in ['Sistem Yöneticisi', 'Yazılım Uzmanı']
        ):
            return True
        
        # Check if the object has a 'user' attribute and the user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # If the object is a user, check if it's the requesting user
        if hasattr(obj, 'username'):
            return obj == request.user
            
        return False

class ReadOnly(permissions.BasePermission):
    """
    Permission to allow only read-only access.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
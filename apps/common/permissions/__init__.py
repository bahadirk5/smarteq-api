from apps.common.permissions.role_permissions import (
    IsSuperUser, IsSystemAdmin, IsSoftwareDeveloper, 
    IsHardwareExpert, IsTechnicalSupport, IsDealerNetwork,
    IsInstitutionManager, IsAdvancedInstitutionManager,
    IsOwnerOrAdmin, ReadOnly, IsAdminOrRoles, IsSystemAdminOrSoftwareDeveloper
)

# Gelecekte eklenecek diğer permission modülleri için import satırları
# from core.permissions.action_permissions import ...
# from core.permissions.object_permissions import ...

# Dışa aktarılan tüm sınıflar
__all__ = [
    'IsSuperUser',
    'IsSystemAdmin',
    'IsSoftwareDeveloper',
    'IsHardwareExpert',
    'IsTechnicalSupport',
    'IsDealerNetwork',
    'IsInstitutionManager',
    'IsAdvancedInstitutionManager',
    'IsOwnerOrAdmin',
    'ReadOnly',
    'IsAdminOrRoles',
    'IsSystemAdminOrSoftwareDeveloper',
    # Gelecekte eklenecek diğer permission sınıfları
]
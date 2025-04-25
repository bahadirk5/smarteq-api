from apps.users.views.department_views import DepartmentViewSet
from apps.users.views.role_views import RoleViewSet
from apps.users.views.user_views import UserViewSet
from apps.users.views.auth_views import (
    CustomTokenObtainPairView, RegisterView, LoginView,
    ChangePasswordView, ResetPasswordRequestView, ResetPasswordConfirmView
)

__all__ = [
    "DepartmentViewSet", "RoleViewSet", "UserViewSet",
    "CustomTokenObtainPairView", "RegisterView", "LoginView",
    "ChangePasswordView", "ResetPasswordRequestView", "ResetPasswordConfirmView"
]
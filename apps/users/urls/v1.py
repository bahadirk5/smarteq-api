from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from apps.users.views import (
    DepartmentViewSet, RoleViewSet, UserViewSet,
    CustomTokenObtainPairView, RegisterView, LoginView,
    ChangePasswordView, ResetPasswordRequestView, ResetPasswordConfirmView
)
from apps.users.views.auth_views import MeView

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('me/', MeView.as_view(), name='users-me'),
    path('', include(router.urls)),
    
    # Auth endpoints
    path('auth/', include([
        path('login/', LoginView.as_view(), name='user-login'),
        path('register/', RegisterView.as_view(), name='user-register'),
        path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),  # Refresh token endpoint
        path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),    # Token doğrulama (isteğe bağlı)
        path('password/change/', ChangePasswordView.as_view(), name='password-change'),
        path('password/reset/', ResetPasswordRequestView.as_view(), name='password-reset-request'),
        path('password/reset/confirm/', ResetPasswordConfirmView.as_view(), name='password-reset-confirm'),
    ])),
]
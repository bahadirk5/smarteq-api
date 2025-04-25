from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.views import (
    DepartmentViewSet, RoleViewSet, UserViewSet,
    CustomTokenObtainPairView, RegisterView, LoginView,
    ChangePasswordView, ResetPasswordRequestView, ResetPasswordConfirmView
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Auth endpoints
    path('auth/', include([
        path('login/', LoginView.as_view(), name='user-login'),
        path('register/', RegisterView.as_view(), name='user-register'),
        path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
        path('password/change/', ChangePasswordView.as_view(), name='password-change'),
        path('password/reset/', ResetPasswordRequestView.as_view(), name='password-reset-request'),
        path('password/reset/confirm/', ResetPasswordConfirmView.as_view(), name='password-reset-confirm'),
    ])),
]
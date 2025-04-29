from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.users.serializers.auth_serializers import (
    CustomTokenObtainPairSerializer, RegisterSerializer, LoginSerializer,
    ChangePasswordSerializer, ResetPasswordRequestSerializer, ResetPasswordConfirmSerializer
)
from apps.users.services import UserService
from rest_framework.views import APIView
from apps.users.serializers.user_serializers import UserSerializer
from apps.common.responses import success_response, error_response

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that returns user information with tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    API view for registering new users.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create and return JWT tokens for the new user
        jwt_serializer = CustomTokenObtainPairSerializer(data={
            'username': serializer.validated_data['username'],
            'password': request.data.get('password')
        })
        jwt_serializer.is_valid(raise_exception=True)
        
        return success_response(
            data={
                'detail': _('User registered successfully.'),
                'tokens': jwt_serializer.validated_data
            }, 
            status_code=status.HTTP_201_CREATED
        )


class LoginView(generics.GenericAPIView):
    """
    API view for logging in users with email or username.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Create and return JWT tokens for the user
        jwt_serializer = CustomTokenObtainPairSerializer(data={
            'username': user.username,
            'password': request.data.get('password')
        })
        jwt_serializer.is_valid(raise_exception=True)
        
        return success_response(data=jwt_serializer.validated_data)


class ChangePasswordView(generics.GenericAPIView):
    """
    API view for changing user password.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if old password is correct
        if not request.user.check_password(serializer.validated_data['old_password']):
            return error_response(
                error_message=_('Wrong password.'),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        
        return success_response(
            data={'detail': _('Password changed successfully.')},
            status_code=status.HTTP_200_OK
        )


class ResetPasswordRequestView(generics.GenericAPIView):
    """
    API view for requesting a password reset.
    """
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordRequestSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # In a real application, send an email with reset link
        # For now, just return a success message
        
        return success_response(
            data={'detail': _('Password reset link has been sent to your email.')},
            status_code=status.HTTP_200_OK
        )


class ResetPasswordConfirmView(generics.GenericAPIView):
    """
    API view for confirming a password reset.
    """
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordConfirmSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # In a real application, verify token and uid and reset password
        # For now, just return a success message
        
        return success_response(
            data={'detail': _('Password has been reset successfully.')},
            status_code=status.HTTP_200_OK
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return success_response(data=serializer.data)
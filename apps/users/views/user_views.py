from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from apps.common.permissions import IsSuperUser, IsSystemAdmin
from apps.common.responses import success_response, error_response
from apps.users.serializers.user_serializers import (
    UserSerializer, UserDetailSerializer, UserCreateSerializer,
    UserUpdateSerializer, PasswordChangeSerializer
)
from apps.users.services import UserService

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_service = UserService()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return PasswordChangeSerializer
        return UserSerializer
    
    def list(self, request, *args, **kwargs):
        # Check for filters
        department_id = request.query_params.get('department')
        role_id = request.query_params.get('role')
        search_query = request.query_params.get('search')
        
        if department_id and role_id:
            users = self.user_service.list_users_by_department_and_role(department_id, role_id)
        elif department_id:
            users = self.user_service.list_users_by_department(department_id)
        elif role_id:
            users = self.user_service.list_users_by_role(role_id)
        elif search_query:
            users = self.user_service.search_users(search_query)
        else:
            users = self.user_service.list_users()
            
        serializer = self.get_serializer(users, many=True)
        return success_response(data=serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        user = self.user_service.get_user(kwargs['pk'])
        if not user:
            return error_response("User not found.", status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(user)
        return success_response(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = dict(serializer.validated_data)
        
        # Extract department and role IDs if present
        department_id = None
        if 'department' in validated_data:
            department = validated_data.pop('department')
            department_id = department.id if department else None
        
        role_id = None
        if 'role' in validated_data:
            role = validated_data.pop('role')
            role_id = role.id if role else None
        
        # Call service to create user
        user = self.user_service.create_user(
            username=validated_data.pop('username'),
            email=validated_data.pop('email'),
            password=validated_data.pop('password'),
            department_id=department_id,
            role_id=role_id,
            **validated_data
        )
        
        if not user:
            return error_response(
                "Could not create user. Department or role may not exist or be incompatible.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return success_response(data=UserSerializer(user).data, status_code=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        user = self.user_service.get_user(kwargs['pk'])
        if not user:
            return error_response("User not found.", status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(user, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        validated_data = dict(serializer.validated_data)
        
        # Extract department and role IDs if present
        if 'department' in validated_data:
            department = validated_data.pop('department')
            validated_data['department_id'] = department.id if department else None
        
        if 'role' in validated_data:
            role = validated_data.pop('role')
            validated_data['role_id'] = role.id if role else None
        
        # Call service to update user
        updated_user = self.user_service.update_user(kwargs['pk'], **validated_data)
        
        if not updated_user:
            return error_response(
                "Could not update user. Department or role may not exist or be incompatible.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return success_response(data=self.get_serializer(updated_user).data)
    
    def destroy(self, request, *args, **kwargs):
        user = self.user_service.get_user(kwargs['pk'])
        if not user:
            return error_response("User not found.", status_code=status.HTTP_404_NOT_FOUND)
        
        # Prevent deleting yourself
        if user.id == request.user.id:
            return error_response(
                "You cannot delete your own account.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Call service to delete user
        success = self.user_service.delete_user(kwargs['pk'])
        if not success:
            return error_response(
                "Failed to delete user.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return success_response(status_code=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        # Get user
        user = self.user_service.get_user(pk)
        if not user:
            return error_response("User not found.", status_code=status.HTTP_404_NOT_FOUND)
        
        # Check permission
        is_admin = request.user.is_staff
        has_permission = self.user_service.check_permission(request.user, pk, is_admin)
        if not has_permission:
            return error_response(
                "You do not have permission to change this user's password.",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check old password if user is changing their own password
        if str(request.user.id) == str(pk):
            old_password_valid = self.user_service.verify_password(user, serializer.validated_data['old_password'])
            if not old_password_valid:
                return error_response({"old_password": ["Wrong password."]}, status_code=status.HTTP_400_BAD_REQUEST)
        
        # Change password
        user = self.user_service.change_password(pk, serializer.validated_data['new_password'])
        
        return success_response({"detail": "Password has been changed successfully."})
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperUser|IsSystemAdmin])
    def set_department(self, request, pk=None):
        if 'department_id' not in request.data:
            return error_response({"detail": "department_id is required."}, status_code=status.HTTP_400_BAD_REQUEST)
        
        # Call service to set department
        user = self.user_service.set_user_department(pk, request.data['department_id'])
        if not user:
            return error_response(
                {"detail": "Could not set department. User or department may not exist."},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return success_response(data=UserSerializer(user).data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperUser|IsSystemAdmin])
    def set_role(self, request, pk=None):
        if 'role_id' not in request.data:
            return error_response({"detail": "role_id is required."}, status_code=status.HTTP_400_BAD_REQUEST)
        
        # Call service to set role
        user = self.user_service.set_user_role(pk, request.data['role_id'])
        if not user:
            return error_response(
                {"detail": "Could not set role. User or role may not exist, or role may not match user's department."},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return success_response(data=UserSerializer(user).data)
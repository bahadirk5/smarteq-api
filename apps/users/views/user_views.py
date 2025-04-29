from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from apps.common.permissions import IsSuperUser, IsSystemAdmin
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
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        user = self.user_service.get_user(kwargs['pk'])
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = dict(serializer.validated_data)
        
        # Extract and convert department and role objects to IDs if present
        department_id = None
        if 'department' in validated_data:
            department = validated_data.pop('department')
            department_id = department.id if department else None
        
        role_id = None
        if 'role' in validated_data:
            role = validated_data.pop('role')
            role_id = role.id if role else None
        
        user = self.user_service.create_user(
            username=validated_data.pop('username'),
            email=validated_data.pop('email'),
            password=validated_data.pop('password'),
            department_id=department_id,
            role_id=role_id,
            **validated_data
        )
        
        if not user:
            return Response(
                {"detail": "Could not create user. Department or role may not exist or be incompatible."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        user = self.user_service.get_user(kwargs['pk'])
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(user, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        # Extract and convert department and role objects to IDs if present
        validated_data = dict(serializer.validated_data)
        if 'department' in validated_data:
            department = validated_data.pop('department')
            validated_data['department_id'] = department.id if department else None
        
        if 'role' in validated_data:
            role = validated_data.pop('role')
            validated_data['role_id'] = role.id if role else None
        
        updated_user = self.user_service.update_user(
            user_id=kwargs['pk'],
            **validated_data
        )
        
        if not updated_user:
            return Response(
                {"detail": "Could not update user. Department or role may not exist or be incompatible."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(UserSerializer(updated_user).data)
    
    def destroy(self, request, *args, **kwargs):
        user = self.user_service.get_user(kwargs['pk'])
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        self.user_service.delete_user(kwargs['pk'])
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change the user's password."""
        user = self.user_service.get_user(pk)
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Only allow users to change their own password or admins to change any password
        if str(request.user.id) != str(pk) and not request.user.is_staff:
            return Response({"detail": "You do not have permission to change this user's password."},
                           status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check old password if user is changing their own password
        if str(request.user.id) == str(pk) and not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({"detail": "Password has been changed successfully."})
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperUser|IsSystemAdmin])
    def set_department(self, request, pk=None):
        """Set the user's department."""
        if 'department_id' not in request.data:
            return Response({"detail": "department_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = self.user_service.set_user_department(pk, request.data['department_id'])
        if not user:
            return Response(
                {"detail": "Could not set department. User or department may not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(UserSerializer(user).data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperUser|IsSystemAdmin])
    def set_role(self, request, pk=None):
        """Set the user's role."""
        if 'role_id' not in request.data:
            return Response({"detail": "role_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = self.user_service.set_user_role(pk, request.data['role_id'])
        if not user:
            return Response(
                {"detail": "Could not set role. User or role may not exist, or role may not match user's department."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(UserSerializer(user).data)
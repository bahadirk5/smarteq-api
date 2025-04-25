from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.users.models import Role
from apps.users.serializers.role_serializers import RoleSerializer, RoleDetailSerializer
from apps.users.serializers.user_serializers import UserSerializer
from apps.users.services import RoleService

class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing roles.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_service = RoleService()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RoleDetailSerializer
        return RoleSerializer
    
    def list(self, request, *args, **kwargs):
        # Check for department filter
        department_id = request.query_params.get('department')
        if department_id:
            roles = self.role_service.list_roles_by_department(department_id)
        else:
            roles = self.role_service.list_roles()
            
        serializer = self.get_serializer(roles, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        role = self.role_service.get_role(kwargs['pk'])
        if not role:
            return Response({"detail": "Role not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(role)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        role = self.role_service.create_role(
            name=serializer.validated_data['name'],
            department_id=serializer.validated_data['department'].id,
            description=serializer.validated_data.get('description')
        )
        
        if not role:
            return Response(
                {"detail": "Could not create role. Department may not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result_serializer = self.get_serializer(role)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        role = self.role_service.get_role(kwargs['pk'])
        if not role:
            return Response({"detail": "Role not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(role, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        # Convert department object to ID if present
        updated_data = dict(serializer.validated_data)
        if 'department' in updated_data:
            updated_data['department_id'] = updated_data.pop('department').id
        
        updated_role = self.role_service.update_role(
            role_id=kwargs['pk'],
            **updated_data
        )
        
        if not updated_role:
            return Response(
                {"detail": "Could not update role. Department may not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result_serializer = self.get_serializer(updated_role)
        return Response(result_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        role = self.role_service.get_role(kwargs['pk'])
        if not role:
            return Response({"detail": "Role not found."}, status=status.HTTP_404_NOT_FOUND)
        
        self.role_service.delete_role(kwargs['pk'])
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get all users assigned to a specific role."""
        role = self.role_service.get_role(pk)
        if not role:
            return Response({"detail": "Role not found."}, status=status.HTTP_404_NOT_FOUND)
        
        users = role.users.filter(deleted_at__isnull=True)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
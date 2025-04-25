from rest_framework import serializers
from apps.users.models.department import Department
from apps.users.models.role import Role

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentDetailSerializer(serializers.ModelSerializer):
    roles_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'is_active', 'deleted_at', 'roles_count', 'users_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def get_roles_count(self, obj):
        return Role.objects.filter(department=obj, deleted_at__isnull=True).count()
    
    def get_users_count(self, obj):
        return obj.users.filter(deleted_at__isnull=True).count()


class DepartmentWithRolesSerializer(serializers.ModelSerializer):
    """Serializer for departments including their associated roles."""
    from apps.users.serializers.role_serializers import RoleSerializer
    
    roles = RoleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'is_active', 'roles']
        read_only_fields = ['id', 'created_at', 'updated_at', 'roles']
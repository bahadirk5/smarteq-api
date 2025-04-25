from rest_framework import serializers
from apps.users.models.role import Role
from apps.users.serializers.department_serializers import DepartmentSerializer

class RoleSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'department', 'department_name', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at', 'department_name']
    
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None


class RoleDetailSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'department', 'created_at', 'updated_at', 'is_active', 'deleted_at', 'users_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def get_users_count(self, obj):
        return obj.users.filter(deleted_at__isnull=True).count()


class RoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name', 'description', 'department']


class RoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name', 'description', 'department', 'is_active']
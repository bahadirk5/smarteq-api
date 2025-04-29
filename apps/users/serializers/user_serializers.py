from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.users.serializers.department_serializers import DepartmentSerializer
from apps.users.serializers.role_serializers import RoleSerializer

# User = get_user_model()
from apps.users.models.user import User 

class UserSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'department', 'department_name', 'role', 'role_name', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'department_name', 'role_name']
    
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None
    
    def get_role_name(self, obj):
        return obj.role.name if obj.role else None


class UserDetailSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'department', 'role', 'is_active', 'date_joined', 'deleted_at'
        ]
        read_only_fields = ['id', 'date_joined', 'deleted_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'department', 'role'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'department', 'role', 'is_active']


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs.pop('new_password_confirm'):
            raise serializers.ValidationError({"new_password_confirm": "New password fields didn't match."})
        return attrs
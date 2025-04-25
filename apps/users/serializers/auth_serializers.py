from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.users.serializers.user_serializers import UserSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that includes user information in response."""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user information to response
        user_serializer = UserSerializer(self.user)
        data['user'] = user_serializer.data
        
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": _("Password fields didn't match.")})
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": _("A user with this email already exists.")})
        
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        user.set_password(validated_data['password'])
        user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login with username/email."""
    
    login = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'}, write_only=True)
    
    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')
        
        if not login or not password:
            raise serializers.ValidationError(_("Please provide both login and password."))
        
        # Check if login is email or username
        if '@' in login:
            try:
                user = User.objects.get(email=login)
            except User.DoesNotExist:
                raise serializers.ValidationError(_("No user found with this email."))
        else:
            try:
                user = User.objects.get(username=login)
            except User.DoesNotExist:
                raise serializers.ValidationError(_("No user found with this username."))
        
        # Authenticate user
        user = authenticate(username=user.username, password=password)
        
        if not user:
            raise serializers.ValidationError(_("Invalid credentials."))
        
        if not user.is_active:
            raise serializers.ValidationError(_("User account is disabled."))
        
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": _("New password fields didn't match.")})
        return attrs


class ResetPasswordRequestSerializer(serializers.Serializer):
    """Serializer for requesting a password reset."""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("No user found with this email address."))
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    """Serializer for confirming a password reset."""
    
    token = serializers.CharField(required=True)
    uid = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": _("Password fields didn't match.")})
        return attrs
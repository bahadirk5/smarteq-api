from typing import List, Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.db.models import Q
from apps.users.repositories.base_repository import BaseRepository

User = get_user_model()

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        try:
            return self.get_queryset().get(username=username)
        except User.DoesNotExist:
            return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        try:
            return self.get_queryset().get(email=email)
        except User.DoesNotExist:
            return None
    
    def list_by_department(self, department_id: int) -> List[User]:
        return list(self.get_queryset().filter(department_id=department_id))
    
    def list_by_role(self, role_id: int) -> List[User]:
        return list(self.get_queryset().filter(role_id=role_id))
    
    def list_by_department_and_role(self, department_id: int, role_id: int) -> List[User]:
        return list(self.get_queryset().filter(department_id=department_id, role_id=role_id))
    
    def create_user(self, username: str, email: str, password: str, **extra_fields) -> User:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
        return user
    
    def create_superuser(self, username: str, email: str, password: str, **extra_fields) -> User:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
        return user
    
    def search(self, query: str) -> List[User]:
        """Search users by username, first_name, last_name, or email."""
        return list(self.get_queryset().filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ))
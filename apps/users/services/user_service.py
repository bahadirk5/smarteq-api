from typing import List, Optional, Dict, Any
from django.contrib.auth import get_user_model
from apps.users.repositories.user_repository import UserRepository
from apps.users.repositories.department_repository import DepartmentRepository
from apps.users.repositories.role_repository import RoleRepository

User = get_user_model()

class UserService:
    def __init__(
        self, 
        user_repository: UserRepository = None,
        department_repository: DepartmentRepository = None,
        role_repository: RoleRepository = None
    ):
        self.user_repository = user_repository or UserRepository()
        self.department_repository = department_repository or DepartmentRepository()
        self.role_repository = role_repository or RoleRepository()
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self.user_repository.get_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.user_repository.get_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repository.get_by_email(email)
    
    def list_users(self) -> List[User]:
        return self.user_repository.list()
    
    def list_users_by_department(self, department_id: int) -> List[User]:
        return self.user_repository.list_by_department(department_id)
    
    def list_users_by_role(self, role_id: int) -> List[User]:
        return self.user_repository.list_by_role(role_id)
    
    def list_users_by_department_and_role(self, department_id: int, role_id: int) -> List[User]:
        return self.user_repository.list_by_department_and_role(department_id, role_id)
    
    def create_user(
        self, 
        username: str, 
        email: str, 
        password: str, 
        department_id: int = None, 
        role_id: int = None,
        **extra_fields
    ) -> Optional[User]:
        # Validate department if provided
        if department_id:
            department = self.department_repository.get_by_id(department_id)
            if not department:
                return None
        
        # Validate role if provided
        if role_id:
            role = self.role_repository.get_by_id(role_id)
            if not role:
                return None
            
            # Ensure role belongs to the department if both are provided
            if department_id and role.department_id != department_id:
                return None
        
        # Create user
        user_data = extra_fields
        if department_id:
            user_data["department_id"] = department_id
        if role_id:
            user_data["role_id"] = role_id
            
        return self.user_repository.create_user(
            username=username,
            email=email,
            password=password,
            **user_data
        )
    
    def update_user(self, user_id: int, **update_data) -> Optional[User]:
        user = self.get_user(user_id)
        if not user:
            return None
        
        # Handle department update
        if "department_id" in update_data:
            department_id = update_data["department_id"]
            if department_id:
                department = self.department_repository.get_by_id(department_id)
                if not department:
                    return None
        
        # Handle role update
        if "role_id" in update_data:
            role_id = update_data["role_id"]
            if role_id:
                role = self.role_repository.get_by_id(role_id)
                if not role:
                    return None
                
                # Check if role and department match if both are being updated
                if "department_id" in update_data and update_data["department_id"]:
                    if role.department_id != update_data["department_id"]:
                        return None
                # Check if role and existing department match if only role is being updated
                elif user.department_id and role.department_id != user.department_id:
                    return None
        
        return self.user_repository.update(user, **update_data)
    
    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        
        return self.user_repository.delete(user)
    
    def set_user_department(self, user_id: int, department_id: int) -> Optional[User]:
        user = self.get_user(user_id)
        if not user:
            return None
        
        department = self.department_repository.get_by_id(department_id)
        if not department:
            return None
        
        # If user has a role, check if it belongs to the new department
        if user.role and user.role.department_id != department_id:
            # Reset the role if it doesn't match the department
            user.role = None
        
        user.department = department
        user.save()
        return user
    
    def set_user_role(self, user_id: int, role_id: int) -> Optional[User]:
        user = self.get_user(user_id)
        if not user:
            return None
        
        role = self.role_repository.get_by_id(role_id)
        if not role:
            return None
        
        # If the user has a department, ensure the role belongs to it
        if user.department and role.department_id != user.department_id:
            return None
        
        # If the user doesn't have a department, set it based on the role
        if not user.department:
            user.department_id = role.department_id
        
        user.role = role
        user.save()
        return user
    
    def search_users(self, query: str) -> List[User]:
        return self.user_repository.search(query)
    
    def change_password(self, user_id: int, new_password: str) -> Optional[User]:
        user = self.get_user(user_id)
        if not user:
            return None
        
        user.set_password(new_password)
        user.save()
        return user
    
    def verify_password(self, user: User, password: str) -> bool:
        return user.check_password(password)
    
    def check_permission(self, user: User, target_user_id: int, is_admin: bool = False) -> bool:
        """Check if user has permission to modify target user"""
        # Admins can modify any user
        if is_admin:
            return True
        
        # Regular users can only modify themselves
        return str(user.id) == str(target_user_id)
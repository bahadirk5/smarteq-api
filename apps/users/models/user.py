from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from apps.users.models.department import Department
from apps.users.models.role import Role

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(
        Department, 
        related_name="users", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Department")
    )
    role = models.ForeignKey(
        Role, 
        related_name="users", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Role")
    )
    deleted_at = models.DateTimeField(_("Deleted At"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def soft_delete(self):
        """Soft delete the user by setting deleted_at timestamp."""
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        """Restore the soft-deleted user."""
        self.deleted_at = None
        self.is_active = True
        self.save()
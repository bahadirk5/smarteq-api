from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class BaseModel(models.Model):
    """
    Abstract base model that provides common fields and functionality.
    
    Fields:
        id: UUID primary key field
        created_at: When the record was created
        updated_at: When the record was last updated
        deleted_at: When the record was soft deleted (null if not deleted)
        is_active: Whether the record is active
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    deleted_at = models.DateTimeField(_("Deleted At"), null=True, blank=True)
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """Soft delete the record by setting deleted_at timestamp."""
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        """Restore the soft-deleted record."""
        self.deleted_at = None
        self.is_active = True
        self.save()
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel
import uuid
import os


def import_file_path(instance, filename):
    """Generate a unique path for uploaded import files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('imports', 'inventory', filename)


class ExcelImport(BaseModel):
    """
    Tracks raw material imports from Excel files.
    """
    IMPORT_TYPES = (
        ('RAW_MATERIALS', _('Raw Materials')),
        ('PRODUCTS', _('Products')),
        ('BOM', _('Bill of Materials')),
        ('ELECTRONIC_COMPONENTS', _('Electronic Components')),
    )
    
    IMPORT_STATUS = (
        ('PENDING', _('Pending')),
        ('PROCESSING', _('Processing')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
    )
    
    import_type = models.CharField(_('Import Type'), max_length=30, choices=IMPORT_TYPES)
    file = models.FileField(_('Excel File'), upload_to=import_file_path)
    status = models.CharField(_('Status'), max_length=20, choices=IMPORT_STATUS, default='PENDING')
    processed_count = models.IntegerField(_('Processed Count'), default=0)
    failed_count = models.IntegerField(_('Failed Count'), default=0)
    error_details = models.TextField(_('Error Details'), blank=True, null=True)
    notes = models.TextField(_('Notes'), blank=True, null=True)
    processed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='excel_imports',
        verbose_name=_('Processed By')
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('Excel Import')
        verbose_name_plural = _('Excel Imports')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_import_type_display()} - {self.created_at} ({self.get_status_display()})"

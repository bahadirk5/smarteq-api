from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class ProductionProcess(BaseModel):
    """
    Represents a specific production job, batch, or phase. Records the actual 
    implementation of the theoretical recipe in BOM.
    """
    STATUS_CHOICES = (
        ('PLANNED', _('Planned')),
        ('IN_PROGRESS', _('In Progress')),
        ('COMPLETED', _('Completed')),
        ('CANCELLED', _('Cancelled')),
    )
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='production_processes',
        verbose_name=_('Project')
    )
    name = models.CharField(_('Name'), max_length=255, help_text=_('Process name or batch number'))
    description = models.TextField(_('Description'), blank=True, null=True)
    process_start_date = models.DateTimeField(_('Process Start Date'), null=True, blank=True)
    process_end_date = models.DateTimeField(_('Process End Date'), null=True, blank=True)
    performed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_processes',
        verbose_name=_('Performed By')
    )
    status = models.CharField(
        _('Status'), 
        max_length=20, 
        choices=STATUS_CHOICES,
        default='PLANNED'
    )
    target_output_item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='target_production_processes',
        verbose_name=_('Target Output Item')
    )
    target_output_quantity = models.IntegerField(
        _('Target Output Quantity')
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('Production Process')
        verbose_name_plural = _('Production Processes')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.project.name}"
    
    @property
    def is_complete(self):
        return self.status == 'COMPLETED'
    
    @property
    def is_in_progress(self):
        return self.status == 'IN_PROGRESS'
    
    @property
    def total_produced_quantity(self):
        return sum(output.quantity_produced for output in self.outputs.all())
    
    @property
    def production_efficiency(self):
        """Calculate production efficiency percentage"""
        if not self.is_complete or self.target_output_quantity <= 0:
            return 0
        
        return (self.total_produced_quantity / self.target_output_quantity) * 100

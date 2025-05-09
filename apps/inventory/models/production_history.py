from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from apps.common.models.base_model import BaseModel

User = get_user_model()


class ProductionHistory(BaseModel):
    """
    Tracks changes to production records for audit purposes.
    """
    production = models.ForeignKey(
        'inventory.Production',
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('Production')
    )
    action = models.CharField(_('Action'), max_length=50)  # Created, Updated, Items Changed, etc.
    performed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='production_history_actions',
        verbose_name=_('Performed By')
    )
    timestamp = models.DateTimeField(_('Timestamp'), auto_now_add=True)
    notes = models.TextField(_('Notes'), blank=True, null=True)
    previous_data = models.JSONField(_('Previous Data'), blank=True, null=True)
    new_data = models.JSONField(_('New Data'), blank=True, null=True)
    
    class Meta(BaseModel.Meta):
        verbose_name = _('Production History')
        verbose_name_plural = _('Production History')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"History: {self.action} on Production {self.production.id} by {self.performed_by.username} at {self.timestamp}"

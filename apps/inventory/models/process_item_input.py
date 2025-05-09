from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class ProcessItemInput(BaseModel):
    """
    Records the materials actually consumed during a specific PRODUCTION_PROCESS.
    """
    process = models.ForeignKey(
        'inventory.ProductionProcess',
        on_delete=models.CASCADE,
        related_name='inputs',
        verbose_name=_('Production Process')
    )
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='process_inputs',
        verbose_name=_('Consumed Item')
    )
    quantity_consumed = models.IntegerField(
        _('Quantity Consumed')
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('Process Item Input')
        verbose_name_plural = _('Process Item Inputs')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.process.name} - {self.item.name} ({self.quantity_consumed})"

from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class ProcessItemOutput(BaseModel):
    """
    Records the products actually produced during a specific PRODUCTION_PROCESS.
    """
    process = models.ForeignKey(
        'inventory.ProductionProcess',
        on_delete=models.CASCADE,
        related_name='outputs',
        verbose_name=_('Production Process')
    )
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='process_outputs',
        verbose_name=_('Produced Item')
    )
    quantity_produced = models.IntegerField(
        _('Quantity Produced')
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('Process Item Output')
        verbose_name_plural = _('Process Item Outputs')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.process.name} - {self.item.name} ({self.quantity_produced})"

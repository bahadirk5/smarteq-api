from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class ProductionItem(BaseModel):
    """
    Records the actual materials consumed during a production event.
    """
    production = models.ForeignKey(
        'inventory.Production',
        on_delete=models.CASCADE,
        related_name='consumed_items',
        verbose_name=_('Production')
    )
    input_item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        related_name='production_consumptions',
        verbose_name=_('Input Item')
    )
    quantity_consumed = models.IntegerField(
        _('Quantity Consumed')
    )
    unit_of_measure = models.CharField(_('Unit of Measure'), max_length=50)
    
    class Meta(BaseModel.Meta):
        verbose_name = _('Production Item')
        verbose_name_plural = _('Production Items')
        ordering = ['production__execution_date', 'id']
    
    def __str__(self):
        return f"Production {self.production.id} - {self.input_item.name} ({self.quantity_consumed} {self.unit_of_measure})"

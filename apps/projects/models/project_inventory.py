from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class ProjectInventory(BaseModel):
    """
    Manages project-specific inventory items.
    Each project can have its own inventory with separate stock levels.
    """
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_('Project')
    )
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='project_inventories',
        verbose_name=_('Item')
    )
    quantity = models.IntegerField(_('Quantity'), default=0)
    minimum_stock_level = models.IntegerField(_('Minimum Stock Level'), default=0)
    notes = models.TextField(_('Notes'), blank=True, null=True)
    
    class Meta(BaseModel.Meta):
        verbose_name = _('Project Inventory')
        verbose_name_plural = _('Project Inventories')
        unique_together = ['project', 'item']
        ordering = ['project__name', 'item__name']
    
    def __str__(self):
        return f"{self.project.name} - {self.item.name} ({self.quantity})"

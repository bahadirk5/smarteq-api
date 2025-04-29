from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class PurchaseOrderLine(BaseModel):
    """
    Represents a line item in a purchase order for a specific product/item.
    """
    purchase_order_id = models.UUIDField(_('Purchase Order ID'))
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='purchase_order_lines',
        verbose_name=_('Item')
    )
    quantity = models.DecimalField(
        _('Quantity'),
        max_digits=10,
        decimal_places=3
    )
    unit_price = models.DecimalField(
        _('Unit Price'),
        max_digits=10,
        decimal_places=2
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('Purchase Order Line')
        verbose_name_plural = _('Purchase Order Lines')
        ordering = ['-created_at']

    def __str__(self):
        return f"Order: {self.purchase_order_id} - {self.item.name} ({self.quantity})"
    
    @property
    def total_price(self):
        """Calculate the total price for this line item"""
        return self.quantity * self.unit_price

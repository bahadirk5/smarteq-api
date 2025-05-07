from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class PurchaseHistory(BaseModel):
    """
    Tracks the purchase history of raw materials including prices and suppliers.
    """
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='purchase_history',
        verbose_name=_('Item')
    )
    purchase_date = models.DateField(_('Purchase Date'))
    quantity = models.DecimalField(_('Quantity'), max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_('Total Price'), max_digits=12, decimal_places=2)
    supplier = models.CharField(_('Supplier'), max_length=255, blank=True, null=True)
    invoice_reference = models.CharField(_('Invoice Reference'), max_length=100, blank=True, null=True)
    notes = models.TextField(_('Notes'), blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = _('Purchase History')
        verbose_name_plural = _('Purchase History')
        ordering = ['-purchase_date']

    def __str__(self):
        return f"{self.item.name} - {self.purchase_date} ({self.quantity} @ {self.unit_price})"
    
    def save(self, *args, **kwargs):
        # Update the total price based on quantity and unit price
        self.total_price = self.quantity * self.unit_price
        
        # Update the item's purchase price and last purchase date
        self.item.purchase_price = self.unit_price
        self.item.last_purchase_date = self.purchase_date
        self.item.save()
        
        super().save(*args, **kwargs)

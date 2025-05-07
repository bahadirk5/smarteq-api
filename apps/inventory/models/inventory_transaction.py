from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class InventoryTransaction(BaseModel):
    """
    Records all inventory movements, including purchases, sales, production inputs/outputs, and adjustments.
    Maintains a transaction history for accurate stock tracking.
    """
    TRANSACTION_TYPES = (
        ('PURCHASE', _('Purchase')),
        ('SALE', _('Sale')),
        ('PRODUCTION_IN', _('Production Input')),
        ('PRODUCTION_OUT', _('Production Output')),
        ('ADJUSTMENT', _('Adjustment')),
        ('TRANSFER', _('Transfer')),
    )
    
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name=_('Item')
    )
    transaction_type = models.CharField(
        _('Transaction Type'),
        max_length=20,
        choices=TRANSACTION_TYPES
    )
    quantity = models.DecimalField(
        _('Quantity'),
        max_digits=10,
        decimal_places=3,
        help_text=_('Positive for additions, negative for deductions')
    )
    transaction_date = models.DateTimeField(_('Transaction Date'), auto_now_add=True)
    reference_model = models.CharField(_('Reference Model'), max_length=100, blank=True, null=True)
    reference_id = models.PositiveIntegerField(_('Reference ID'), blank=True, null=True)
    notes = models.TextField(_('Notes'), blank=True, null=True)
    
    class Meta(BaseModel.Meta):
        verbose_name = _('Inventory Transaction')
        verbose_name_plural = _('Inventory Transactions')
        ordering = ['-transaction_date']
        
    def __str__(self):
        return f"{self.transaction_type} - {self.item.name} ({self.quantity})"

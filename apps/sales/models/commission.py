from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class CommissionType(models.TextChoices):
    """Commission type choices"""
    SMARTEQ = 'smarteq', _('SmartEQ')
    THIRD_PARTY = 'third_party', _('Third Party')
    DEALER = 'dealer', _('Dealer')


class OrderCommission(BaseModel):
    """
    Order Commission model for tracking commissions related to orders.
    
    Fields:
        order: The order this commission belongs to
        commission_type: Type of commission (SmartEQ, Third Party, or Dealer)
        unit_amount: Commission amount per unit
        quantity: Number of units for commission calculation
        is_collected: Whether the commission has been collected
        third_party_name: Name of the third party (if applicable)
    """
    order = models.ForeignKey(
        'sales.Order',
        on_delete=models.CASCADE,
        related_name='commissions',
        verbose_name=_('Order')
    )
    commission_type = models.CharField(
        _('Commission Type'),
        max_length=20,
        choices=CommissionType.choices,
        default=CommissionType.SMARTEQ
    )
    unit_amount = models.DecimalField(
        _('Unit Amount'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    quantity = models.IntegerField(
        _('Quantity'),
        null=True,
        blank=True
    )
    is_collected = models.BooleanField(
        _('Is Collected'),
        default=False
    )
    third_party_name = models.CharField(
        _('Third Party Name'),
        max_length=255,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('Order Commission')
        verbose_name_plural = _('Order Commissions')
    
    def __str__(self):
        return f"{self.get_commission_type_display()} Commission for {self.order.order_number}"
    
    @property
    def total_amount(self):
        """Calculate the total commission amount"""
        if self.unit_amount is None or self.quantity is None:
            return 0
        return self.unit_amount * self.quantity
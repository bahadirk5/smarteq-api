from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel
from datetime import date, timedelta


class Device(BaseModel):
    """
    Device model for storing device information and warranty details.
    Connected with the Item inventory model for tracking finished products.
    
    Fields:
        item: Connection to the Item model in inventory
        serial_number: Unique serial number of the device
        purchase_date: Date when the device was purchased
        warranty_period_months: Warranty period in months
        notes: Additional notes about the device
    """
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name=_('Item'),
        help_text=_('The finished product this device instance represents')
    )
    serial_number = models.CharField(_("Serial Number"), max_length=100, unique=True)
    purchase_date = models.DateField(_("Purchase Date"), blank=True, null=True)
    warranty_period_months = models.PositiveIntegerField(_("Warranty Period (Months)"), default=24)
    notes = models.TextField(_("Notes"), blank=True, null=True)
    
    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
    
    def __str__(self):
        return f"{self.item.name} - {self.serial_number}"
    
    @property
    def warranty_end_date(self):
        """Calculate warranty end date"""
        if not self.purchase_date:
            return None
        return self.purchase_date + timedelta(days=30 * self.warranty_period_months)
    
    @property
    def is_in_warranty(self):
        """Check if device is still in warranty"""
        if not self.purchase_date:
            return False
        return date.today() <= self.warranty_end_date
    
    @property
    def remaining_warranty_days(self):
        """Calculate remaining warranty days"""
        if not self.purchase_date or not self.is_in_warranty:
            return 0
        return (self.warranty_end_date - date.today()).days
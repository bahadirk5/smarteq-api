from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class RepairPart(BaseModel):
    """
    Repair Part model for tracking spare parts used in repairs.
    
    Fields:
        repair_request: The repair request this part is used for
        item: The inventory item used as spare part
        quantity: Number of parts used
        unit_price: Unit price of the part
        total_price: Total price for this part
        is_warranty_covered: Whether this part is covered by warranty
    """
    repair_request = models.ForeignKey(
        'service.RepairRequest',
        on_delete=models.CASCADE,
        related_name='repair_parts',
        verbose_name=_('Repair Request')
    )
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        related_name='used_in_repairs',
        verbose_name=_('Spare Part')
    )
    quantity = models.PositiveIntegerField(_("Quantity"), default=1)
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_("Total Price"), max_digits=10, decimal_places=2)
    is_warranty_covered = models.BooleanField(_("Is Warranty Covered"), default=True)
    
    class Meta:
        verbose_name = _("Repair Part")
        verbose_name_plural = _("Repair Parts")
    
    def __str__(self):
        return f"{self.item.name} ({self.quantity}) - Repair #{self.repair_request.id}"
    
    def save(self, *args, **kwargs):
        # Calculate total price before saving
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # If not covered by warranty, update the repair request cost
        if not self.is_warranty_covered and self.repair_request:
            self.update_repair_request_cost()
    
    def update_repair_request_cost(self):
        """Update the repair request's total cost based on non-warranty parts"""
        repair = self.repair_request
        non_warranty_parts = RepairPart.objects.filter(
            repair_request=repair,
            is_warranty_covered=False
        )
        total_parts_cost = sum(part.total_price for part in non_warranty_parts)
        repair.repair_cost = total_parts_cost
        repair.save(update_fields=['repair_cost'])
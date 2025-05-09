from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class QuotationStatus(models.TextChoices):
    """Quotation status choices"""
    DRAFT = 'draft', _('Draft')
    SENT = 'sent', _('Sent')
    ACCEPTED = 'accepted', _('Accepted')
    REJECTED = 'rejected', _('Rejected')
    EXPIRED = 'expired', _('Expired')


class Quotation(BaseModel):
    """
    Quotation model for storing price quotations for dealers.
    
    Fields:
        quotation_number: Unique number for the quotation
        dealer: The dealer this quotation is for
        issue_date: Date when the quotation was issued
        valid_until: Date until which the quotation is valid
        status: Current status of the quotation
        total_price: Total price of the quotation
        pdf_file: The generated PDF file for this quotation
        notes: Additional notes about the quotation
    """
    quotation_number = models.CharField(_("Quotation Number"), max_length=50, unique=True)
    dealer = models.ForeignKey(
        'dealers.Dealer',
        on_delete=models.CASCADE,
        related_name='quotations',
        verbose_name=_('Dealer')
    )
    issue_date = models.DateField(_("Issue Date"), auto_now_add=True)
    valid_until = models.DateField(_("Valid Until"))
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=QuotationStatus.choices,
        default=QuotationStatus.DRAFT
    )
    total_price = models.DecimalField(_("Total Price"), max_digits=10, decimal_places=2, default=0)
    pdf_file = models.FileField(_("PDF File"), upload_to='quotations/', blank=True, null=True)
    notes = models.TextField(_("Notes"), blank=True, null=True)
    
    class Meta:
        verbose_name = _("Quotation")
        verbose_name_plural = _("Quotations")
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"Quotation #{self.quotation_number} - {self.dealer.name}"
    
    def calculate_total_price(self):
        """Calculate total price from quotation items"""
        total = sum(item.total_price for item in self.items.all())
        self.total_price = total
        self.save(update_fields=['total_price'])
        return total
    
    @property
    def is_valid(self):
        """Check if quotation is still valid"""
        from datetime import date
        return self.valid_until >= date.today()


class QuotationItem(BaseModel):
    """
    Quotation Item model for storing individual items in a quotation.
    
    Fields:
        quotation: The quotation this item belongs to
        item: The inventory item being quoted
        quantity: Number of items quoted
        unit_price: Price per unit
        total_price: Total price for this line item
        discount_percent: Discount percentage applied to this item
    """
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Quotation')
    )
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='quotation_items',
        verbose_name=_('Item')
    )
    quantity = models.PositiveIntegerField(_("Quantity"))
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(_("Discount %"), max_digits=5, decimal_places=2, default=0)
    total_price = models.DecimalField(_("Total Price"), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _("Quotation Item")
        verbose_name_plural = _("Quotation Items")
    
    def __str__(self):
        return f"{self.item.name} ({self.quantity}) - {self.quotation.quotation_number}"
    
    def save(self, *args, **kwargs):
        # Calculate total price with discount before saving
        discounted_unit_price = self.unit_price * (1 - (self.discount_percent / 100))
        self.total_price = self.quantity * discounted_unit_price
        super().save(*args, **kwargs)
        
        # Update quotation total
        self.quotation.calculate_total_price()
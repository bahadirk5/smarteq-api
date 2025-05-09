from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class RepairStatus(models.TextChoices):
    """Repair status choices"""
    CREATED = 'created', _('Created')  # Oluşturuldu
    RECEIVED = 'received', _('Received')  # Teslim Alındı
    FEE_NOTIFIED = 'fee_notified', _('Fee Notified')  # Ücret Bildirildi
    DEALER_APPROVED = 'dealer_approved', _('Dealer Approved')  # Bayi Onayladı
    PAYMENT_PENDING = 'payment_pending', _('Payment Pending')  # Ödeme Bekleniyor
    REPAIRING = 'repairing', _('Repairing')  # Onarım Aşamasında
    READY_FOR_DELIVERY = 'ready_for_delivery', _('Ready For Delivery')  # Teslime Hazır
    DELIVERED_TO_DEALER = 'delivered_to_dealer', _('Delivered To Dealer')  # Bayi Teslim


class RepairRequest(BaseModel):
    """
    Repair Request model for tracking device repairs.
    
    Fields:
        device: The device that needs repair
        dealer: The dealer who submitted the repair request
        customer: The end customer who owns the device
        request_date: Date when the repair request was submitted
        issue_description: Description of the issue with the device
        status: Current status of the repair request
        technician_notes: Internal notes from the technician
        is_warranty: Whether the repair is covered by warranty
        repair_cost: Cost of the repair (if not under warranty)
        completion_date: Date when the repair was completed
    """
    device = models.ForeignKey(
        'sales.Device',
        on_delete=models.CASCADE,
        related_name='repair_requests',
        verbose_name=_('Device')
    )
    dealer = models.ForeignKey(
        'dealers.Dealer',
        on_delete=models.CASCADE,
        related_name='repair_requests',
        verbose_name=_('Dealer')
    )
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='repair_requests',
        verbose_name=_('Customer')
    )
    request_date = models.DateField(_("Request Date"), auto_now_add=True)
    issue_description = models.TextField(_("Issue Description"))
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=RepairStatus.choices,
        default=RepairStatus.CREATED
    )
    technician_notes = models.TextField(_("Technician Notes"), blank=True, null=True)
    is_warranty = models.BooleanField(_("Is Warranty"), default=True)
    repair_cost = models.DecimalField(
        _("Repair Cost"), 
        max_digits=10, 
        decimal_places=2, 
        default=0,
        null=True,
        blank=True
    )
    completion_date = models.DateField(_("Completion Date"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Repair Request")
        verbose_name_plural = _("Repair Requests")
        ordering = ['-request_date']
    
    def __str__(self):
        return f"Repair #{self.id} - {self.device.serial_number}"
    
    def save(self, *args, **kwargs):
        # Check if device is in warranty and set is_warranty accordingly
        if not self.id:  # Only during first save
            self.is_warranty = self.device.is_in_warranty
        super().save(*args, **kwargs)
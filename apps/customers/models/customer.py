from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class CustomerType(models.TextChoices):
    """Customer type choices"""
    INDIVIDUAL = 'individual', _('Individual')
    CORPORATE = 'corporate', _('Corporate')


class Customer(BaseModel):
    """
    Customer model for storing customer information.
    
    Fields:
        name: Name of the customer or company
        customer_type: Type of customer (individual or corporate)
        contact_person: Name of the primary contact person (for corporate customers)
        email: Email address of the customer
        phone: Phone number of the customer
        address: Physical address of the customer
        tax_id: Tax identification number (for corporate customers)
        tax_office: Tax office name (for corporate customers)
        dealer: The dealer associated with this customer
        notes: Additional notes about the customer
    """
    name = models.CharField(_("Name"), max_length=255)
    customer_type = models.CharField(
        _("Customer Type"),
        max_length=20,
        choices=CustomerType.choices,
        default=CustomerType.INDIVIDUAL
    )
    contact_person = models.CharField(_("Contact Person"), max_length=255, blank=True, null=True)
    email = models.EmailField(_("Email"), max_length=255, blank=True, null=True)
    phone = models.CharField(_("Phone"), max_length=20, blank=True, null=True)
    address = models.TextField(_("Address"), blank=True, null=True)
    tax_id = models.CharField(_("Tax ID"), max_length=20, blank=True, null=True)
    tax_office = models.CharField(_("Tax Office"), max_length=100, blank=True, null=True)
    dealer = models.ForeignKey(
        'dealers.Dealer',
        verbose_name=_("Dealer"),
        on_delete=models.CASCADE,
        related_name="customers"
    )
    notes = models.TextField(_("Notes"), blank=True, null=True)
    
    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
    
    def __str__(self):
        return self.name
    
    @property
    def is_corporate(self):
        """Check if customer is corporate"""
        return self.customer_type == CustomerType.CORPORATE
    
    @property
    def is_individual(self):
        """Check if customer is individual"""
        return self.customer_type == CustomerType.INDIVIDUAL
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class Dealer(BaseModel):
    """
    Dealer model for storing dealer information.
    
    Fields:
        name: Name of the dealer
        code: Unique code to identify the dealer
        contact_person: Name of the primary contact person
        email: Email address of the dealer
        phone: Phone number of the dealer
        address: Physical address of the dealer
        tax_id: Tax identification number
        tax_office: Tax office name
        notes: Additional notes about the dealer
    """
    name = models.CharField(_("Name"), max_length=255)
    code = models.CharField(_("Code"), max_length=50, unique=True)
    contact_person = models.CharField(_("Contact Person"), max_length=255, blank=True, null=True)
    email = models.EmailField(_("Email"), max_length=255, blank=True, null=True)
    phone = models.CharField(_("Phone"), max_length=20, blank=True, null=True)
    address = models.TextField(_("Address"), blank=True, null=True)
    tax_id = models.CharField(_("Tax ID"), max_length=20, blank=True, null=True)
    tax_office = models.CharField(_("Tax Office"), max_length=100, blank=True, null=True)
    notes = models.TextField(_("Notes"), blank=True, null=True)
    
    class Meta:
        verbose_name = _("Dealer")
        verbose_name_plural = _("Dealers")
    
    def __str__(self):
        return self.name
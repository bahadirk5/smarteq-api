from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class Item(BaseModel):
    """
    Central model representing all physical or virtual items in the system 
    (Raw Materials, Intermediate Products, Final Products).
    """
    ITEM_TYPES = (
        ('RAW', _('Raw Material')),
        ('INTERMEDIATE', _('Intermediate Product')),
        ('FINAL', _('Final Product')),
    )
    
    name = models.CharField(_('Name'), max_length=255)
    sku = models.CharField(_('SKU'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    item_type = models.CharField(_('Item Type'), max_length=20, choices=ITEM_TYPES)
    category = models.ForeignKey(
        'inventory.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
        verbose_name=_('Category')
    )
    unit_of_measure = models.CharField(_('Unit of Measure'), max_length=50)
    cost_price = models.DecimalField(_('Cost Price'), max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(_('Selling Price'), max_digits=10, decimal_places=2, default=0)

    class Meta(BaseModel.Meta):
        verbose_name = _('Item')
        verbose_name_plural = _('Items')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def is_raw_material(self):
        return self.item_type == 'RAW'
    
    @property
    def is_intermediate_product(self):
        return self.item_type == 'INTERMEDIATE'
    
    @property
    def is_final_product(self):
        return self.item_type == 'FINAL'

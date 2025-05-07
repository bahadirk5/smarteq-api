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
    
    SALES_LIST_STATUS = (
        ('NOT_LISTED', _('Not Listed')),
        ('CUSTOMER_LIST', _('Customer Sales List')),
        ('DEALER_LIST', _('Dealer Sales List')),
        ('BOTH_LISTS', _('Both Sales Lists')),
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
    quantity = models.IntegerField(_('Quantity'), default=0)
    minimum_stock_level = models.IntegerField(_('Minimum Stock Level'), default=0)
    purchase_price = models.DecimalField(_('Purchase Price'), max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(_('Selling Price'), max_digits=10, decimal_places=2, default=0)
    dealer_price = models.DecimalField(_('Dealer Price'), max_digits=10, decimal_places=2, default=0)
    sales_list_status = models.CharField(
        _('Sales List Status'), 
        max_length=20, 
        choices=SALES_LIST_STATUS,
        default='NOT_LISTED'
    )
    last_purchase_date = models.DateField(_('Last Purchase Date'), null=True, blank=True)
    
    # Excel structure specific field for component references (R6, R7, C183, etc.)
    reference = models.CharField(_('Reference'), max_length=255, blank=True, null=True)
    # Track order status for inventory management
    order_status = models.BooleanField(_('Order Status'), default=False)
    
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
    
    @property
    def is_in_customer_list(self):
        return self.sales_list_status in ['CUSTOMER_LIST', 'BOTH_LISTS']
    
    @property
    def is_in_dealer_list(self):
        return self.sales_list_status in ['DEALER_LIST', 'BOTH_LISTS']

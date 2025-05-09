from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class OrderStatus(models.TextChoices):
    """Order status choices"""
    PENDING = 'pending', _('Pending')
    CONFIRMED = 'confirmed', _('Confirmed')
    PROCESSING = 'processing', _('Processing')
    SHIPPED = 'shipped', _('Shipped')
    DELIVERED = 'delivered', _('Delivered')
    CANCELLED = 'cancelled', _('Cancelled')


class CurrencyType(models.TextChoices):
    """Currency type choices"""
    TRY = 'try', _('Turkish Lira')
    USD = 'usd', _('US Dollar')
    EUR = 'eur', _('Euro')


class Order(BaseModel):
    """
    Order model for storing dealer orders.
    
    Fields:
        order_number: Unique number for the order
        dealer: The dealer that placed the order
        order_date: Date when the order was placed
        status: Current status of the order
        is_paid: Whether the order has been paid
        shipping_address: Address where the order will be shipped
        shipping_date: Date when the order was shipped
        delivery_date: Date when the order was delivered
        completion_date: Date when the order was completed
        total_price: Total price of the order
        currency: Currency of the order
        device_set_count: Number of device sets in the order
        notes: Additional notes about the order
    """
    order_number = models.CharField(_("Order Number"), max_length=50, unique=True)
    dealer = models.ForeignKey(
        'dealers.Dealer',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Dealer')
    )
    order_date = models.DateField(_("Order Date"), auto_now_add=True)
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    is_paid = models.BooleanField(_("Is Paid"), default=False)
    shipping_address = models.TextField(_("Shipping Address"), blank=True, null=True)
    shipping_date = models.DateField(_("Shipping Date"), blank=True, null=True)
    delivery_date = models.DateField(_("Delivery Date"), blank=True, null=True)
    completion_date = models.DateField(_("Completion Date"), blank=True, null=True)
    total_price = models.DecimalField(_("Total Price"), max_digits=10, decimal_places=2, default=0)
    vat_amount = models.DecimalField(_("VAT Amount"), max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(_("Grand Total"), max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(
        _("Currency"),
        max_length=3,
        choices=CurrencyType.choices,
        default=CurrencyType.TRY
    )
    device_set_count = models.PositiveIntegerField(_("Device Set Count"), default=1)
    notes = models.TextField(_("Notes"), blank=True, null=True)
    
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.dealer.name}"
    
    def calculate_total_price(self):
        """Calculate total price from order items"""
        total = sum(item.total_price for item in self.items.all())
        self.total_price = total
        
        # Calculate VAT and grand total
        self.calculate_vat()
        super().save(update_fields=['total_price', 'vat_amount', 'grand_total'])
        return total
    
    def calculate_vat(self):
        """Calculate VAT amount and grand total"""
        # Calculate VAT amount from items
        self.vat_amount = sum(item.vat_amount for item in self.items.all())
        # Grand total is the sum of total price and VAT amount
        self.grand_total = self.total_price + self.vat_amount
        return self.vat_amount


class OrderItem(BaseModel):
    """
    Order Item model for storing individual items in an order.
    
    Fields:
        order: The order this item belongs to
        item: The inventory item being ordered
        quantity: Number of items ordered
        unit_price: Original price per unit
        discount_percentage: Discount percentage for this item
        dealer_discount_percentage: Additional dealer discount percentage
        discounted_price: Price after applying discounts
        vat_percentage: VAT percentage to apply
        vat_amount: VAT amount for this item
        total_price: Total price for this line item (after discounts, before VAT)
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Order')
    )
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name=_('Item')
    )
    quantity = models.PositiveIntegerField(_("Quantity"))
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(_("Discount %"), max_digits=5, decimal_places=2, default=0)
    dealer_discount_percentage = models.DecimalField(_("Dealer Discount %"), max_digits=5, decimal_places=2, default=0)
    discounted_price = models.DecimalField(_("Discounted Price"), max_digits=10, decimal_places=2)
    vat_percentage = models.DecimalField(_("VAT %"), max_digits=5, decimal_places=2, default=18)
    vat_amount = models.DecimalField(_("VAT Amount"), max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(_("Total Price"), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
    
    def __str__(self):
        return f"{self.item.name} ({self.quantity}) - {self.order.order_number}"
    
    def calculate_discounted_price(self):
        """Calculate discounted price after applying both discounts"""
        # First apply the regular discount
        price_after_discount = self.unit_price * (1 - (self.discount_percentage / 100))
        # Then apply the dealer discount
        self.discounted_price = price_after_discount * (1 - (self.dealer_discount_percentage / 100))
        return self.discounted_price
    
    def calculate_vat_amount(self):
        """Calculate VAT amount for this item"""
        self.vat_amount = (self.discounted_price * self.quantity) * (self.vat_percentage / 100)
        return self.vat_amount
    
    def calculate_total_price(self):
        """Calculate the total price (discounted price × quantity)"""
        self.total_price = self.discounted_price * self.quantity
        return self.total_price
    
    def save(self, *args, **kwargs):
        # Calculate all prices and amounts before saving
        self.calculate_discounted_price()
        self.calculate_total_price()
        self.calculate_vat_amount()
        super().save(*args, **kwargs)
        
        # Update order total
        self.order.calculate_total_price()
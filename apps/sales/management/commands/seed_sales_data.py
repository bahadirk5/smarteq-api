from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal
import random

from apps.sales.models import Order, OrderItem, OrderStatus, CurrencyType, Device
from apps.dealers.models import Dealer
from apps.inventory.models import Item
from apps.customers.models import Customer

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample sales data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting sales data seeding...'))
        
        try:
            with transaction.atomic():
                self.create_devices()
                self.create_orders()
                
            self.stdout.write(self.style.SUCCESS('Successfully seeded sales data!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding data: {str(e)}'))
    
    def create_devices(self):
        self.stdout.write('Creating device records...')
        
        # Get or check for finished products in inventory
        try:
            # Get a few finished products from inventory
            finished_products = Item.objects.filter(item_type='FINAL')[:5]
            if not finished_products:
                self.stdout.write(self.style.WARNING(
                    'No finished products found in inventory. '
                    'Please run the seed_inventory_data command first.'
                ))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting finished products: {str(e)}'))
            return
        
        # Create device records for inventory items
        for idx, product in enumerate(finished_products):
            # Create multiple devices for each product
            for i in range(1, 11):  # Create 10 devices per product
                purchase_date = None
                if i <= 7:  # 70% of devices are sold
                    # Randomly set purchase date within the last year
                    days_ago = random.randint(1, 365)
                    purchase_date = date.today() - timedelta(days=days_ago)
                
                Device.objects.create(
                    item=product,
                    serial_number=f"{product.sku}-{idx+1}-{i:04d}",
                    purchase_date=purchase_date,
                    warranty_period_months=24,  # 2 year warranty
                    notes=f"Sample device for {product.name}"
                )
        
        self.stdout.write(self.style.SUCCESS('Devices created successfully!'))
    
    def create_orders(self):
        self.stdout.write('Creating orders...')
        
        # Get dealers or check they exist
        try:
            dealers = Dealer.objects.all()[:5]
            if not dealers:
                self.stdout.write(self.style.WARNING(
                    'No dealers found. Please run the seed_dealers_data command first.'
                ))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting dealers: {str(e)}'))
            return
        
        # Get inventory items
        try:
            inventory_items = Item.objects.filter(item_type='FINAL')[:5]
            if not inventory_items:
                self.stdout.write(self.style.WARNING('No inventory items found.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting inventory items: {str(e)}'))
            return
        
        # Create orders with different statuses
        statuses = list(OrderStatus.choices)
        currencies = list(CurrencyType.choices)
        
        for i in range(1, 11):  # Create 10 sample orders
            # Select a random dealer
            dealer = random.choice(dealers)
            
            # Create order with random details
            order_date = date.today() - timedelta(days=random.randint(0, 90))
            status = random.choice(statuses)[0]
            currency = random.choice(currencies)[0]
            
            order = Order.objects.create(
                order_number=f"ORD-{timezone.now().year}-{i:04d}",
                dealer=dealer,
                order_date=order_date,
                status=status,
                is_paid=(status in [OrderStatus.DELIVERED, OrderStatus.SHIPPED]),
                shipping_address=dealer.address,
                currency=currency,
                device_set_count=random.randint(1, 5),
                notes=f"Sample order for {dealer.name}"
            )
            
            # Set dates based on status
            if status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
                order.shipping_date = order_date + timedelta(days=3)
            
            if status == OrderStatus.DELIVERED:
                order.delivery_date = order_date + timedelta(days=7)
                order.completion_date = order_date + timedelta(days=8)
            
            order.save()
            
            # Add 1-4 items to order
            num_items = random.randint(1, 4)
            for j in range(num_items):
                item = random.choice(inventory_items)
                quantity = random.randint(1, 5)
                unit_price = item.selling_price
                discount_percentage = Decimal(random.randint(0, 15))
                dealer_discount_percentage = Decimal(random.randint(0, 10))
                
                OrderItem.objects.create(
                    order=order,
                    item=item,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount_percentage=discount_percentage,
                    dealer_discount_percentage=dealer_discount_percentage,
                    discounted_price=unit_price,  # Will be calculated on save
                    vat_percentage=Decimal('18.00'),  # Standard VAT rate
                    total_price=unit_price * quantity  # Will be calculated on save
                )
        
        self.stdout.write(self.style.SUCCESS('Orders created successfully!'))
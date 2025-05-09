from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal
import random

from apps.service.models import RepairRequest, RepairStatus, RepairPart
from apps.sales.models import Device
from apps.dealers.models import Dealer
from apps.customers.models import Customer
from apps.inventory.models import Item

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample service data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting service data seeding...'))
        
        try:
            with transaction.atomic():
                self.create_repair_requests()
                
            self.stdout.write(self.style.SUCCESS('Successfully seeded service data!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding data: {str(e)}'))
    
    def create_repair_requests(self):
        self.stdout.write('Creating repair requests...')
        
        # Get devices that are already sold (have purchase date)
        try:
            devices = Device.objects.filter(purchase_date__isnull=False)[:20]
            if not devices:
                self.stdout.write(self.style.WARNING(
                    'No purchased devices found. Please run the seed_sales_data command first.'
                ))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting devices: {str(e)}'))
            return
        
        # Get dealers
        try:
            dealers = Dealer.objects.all()[:5]
            if not dealers:
                self.stdout.write(self.style.WARNING('No dealers found.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting dealers: {str(e)}'))
            return
        
        # Get customers
        try:
            customers = Customer.objects.all()[:10]
            if not customers:
                self.stdout.write(self.style.WARNING('No customers found.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting customers: {str(e)}'))
            return
        
        # Get components/parts for repairs
        try:
            components = Item.objects.filter(item_type='INTERMEDIATE')[:10]
            if not components:
                self.stdout.write(self.style.WARNING('No component items found for repairs.'))
                # We'll continue anyway, just won't add repair parts
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting components: {str(e)}'))
            components = []
        
        # List of common issues for randomization
        common_issues = [
            "Device not powering on",
            "Screen display malfunction",
            "Connection issues with WiFi",
            "Sensor not responding accurately",
            "Battery draining too quickly",
            "Software crashes frequently",
            "Physical damage to enclosure",
            "Button malfunction",
            "Overheating during operation",
            "Unusual noise during operation"
        ]
        
        # Create repair requests for some devices
        repair_count = min(15, len(devices))  # Create up to 15 repair requests
        for i in range(repair_count):
            # Select a random device
            device = devices[i]
            
            # Check which dealer to associate
            device_dealer = device.item.orders.first().dealer if hasattr(device, 'orders') and device.item.orders.exists() else random.choice(dealers)
            
            # Select random customer
            customer = random.choice(customers)
            
            # Random request date after purchase date but before today
            days_after_purchase = random.randint(30, 300)  # Between 1 month and 10 months after purchase
            if device.purchase_date:
                request_date = min(
                    date.today(),
                    device.purchase_date + timedelta(days=days_after_purchase)
                )
            else:
                request_date = date.today() - timedelta(days=random.randint(1, 90))
            
            # Random status
            status = random.choice(list(RepairStatus.choices))[0]
            
            # Determine if in warranty based on purchase date and warranty period
            is_warranty = device.is_in_warranty if hasattr(device, 'is_in_warranty') else True
            
            # Set completion date if status indicates it's done
            completion_date = None
            if status in [RepairStatus.DELIVERED_TO_DEALER, RepairStatus.READY_FOR_DELIVERY]:
                completion_date = request_date + timedelta(days=random.randint(3, 14))
            
            # Create the repair request
            repair_request = RepairRequest.objects.create(
                device=device,
                dealer=device_dealer,
                customer=customer,
                request_date=request_date,
                issue_description=random.choice(common_issues),
                status=status,
                technician_notes=f"Sample technician notes for repair #{i+1}" if random.random() > 0.3 else None,
                is_warranty=is_warranty,
                repair_cost=Decimal('0.00'),  # Will be updated based on parts
                completion_date=completion_date
            )
            
            # Add repair parts if we have components and it's a valid repair status
            if components and status not in [RepairStatus.CREATED, RepairStatus.RECEIVED]:
                # Add 1-3 repair parts
                num_parts = random.randint(1, 3)
                for j in range(num_parts):
                    component = random.choice(components)
                    quantity = random.randint(1, 2)
                    unit_price = component.selling_price or Decimal('10.00')  # Default if no price
                    
                    # Determine if part is covered by warranty
                    is_part_warranty_covered = is_warranty and random.random() < 0.8  # 80% chance if in warranty
                    
                    RepairPart.objects.create(
                        repair_request=repair_request,
                        item=component,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=unit_price * quantity,  # Will be calculated on save
                        is_warranty_covered=is_part_warranty_covered
                    )
        
        self.stdout.write(self.style.SUCCESS(f'Created {repair_count} repair requests successfully!'))
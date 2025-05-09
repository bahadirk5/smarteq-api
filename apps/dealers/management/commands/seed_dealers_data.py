from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.dealers.models import Dealer

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample dealers data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting dealers data seeding...'))
        
        try:
            with transaction.atomic():
                self.create_dealers()
                
            self.stdout.write(self.style.SUCCESS('Successfully seeded dealers data!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding data: {str(e)}'))
    
    def create_dealers(self):
        self.stdout.write('Creating dealers...')
        
        # Create dealers
        dealer1 = Dealer.objects.create(
            name='Tech Solutions Inc.',
            code='TECH001',
            contact_person='John Smith',
            email='john@techsolutions.com',
            phone='(555) 123-4567',
            address='123 Tech Street, Istanbul, Turkey',
            tax_id='1234567890',
            tax_office='Istanbul Corporate Tax Office',
            notes='Premium tier dealer with excellent performance'
        )
        
        dealer2 = Dealer.objects.create(
            name='Smart Systems Ltd.',
            code='SMART002',
            contact_person='Maria Rodriguez',
            email='maria@smartsystems.com',
            phone='(555) 987-6543',
            address='456 Innovation Avenue, Ankara, Turkey',
            tax_id='0987654321',
            tax_office='Ankara Tax Office',
            notes='Mid-tier dealer with growing sales'
        )
        
        dealer3 = Dealer.objects.create(
            name='Connected Devices Co.',
            code='CONN003',
            contact_person='Ahmet Yilmaz',
            email='ahmet@connecteddevices.com',
            phone='(555) 456-7890',
            address='789 IoT Boulevard, Izmir, Turkey',
            tax_id='5678901234',
            tax_office='Izmir Tax Office',
            notes='New dealer specializing in smart home installations'
        )
        
        dealer4 = Dealer.objects.create(
            name='Elite Electronics',
            code='ELITE004',
            contact_person='Fatma Demir',
            email='fatma@eliteelectronics.com',
            phone='(555) 321-0987',
            address='101 Elite Street, Antalya, Turkey',
            tax_id='3456789012',
            tax_office='Antalya Tax Office',
            notes='Focus on high-end customers and solutions'
        )
        
        dealer5 = Dealer.objects.create(
            name='Value Tech Distributors',
            code='VALUE005',
            contact_person='Mehmet Kaya',
            email='mehmet@valuetech.com',
            phone='(555) 234-5678',
            address='202 Value Road, Bursa, Turkey',
            tax_id='6789012345',
            tax_office='Bursa Tax Office',
            notes='High volume dealer with competitive pricing'
        )
        
        self.stdout.write(self.style.SUCCESS('Dealers created successfully!'))
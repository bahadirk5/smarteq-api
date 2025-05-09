from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.customers.models import Customer, CustomerType
from apps.dealers.models import Dealer

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample customers data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting customers data seeding...'))
        
        try:
            with transaction.atomic():
                self.create_customers()
                
            self.stdout.write(self.style.SUCCESS('Successfully seeded customers data!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding data: {str(e)}'))
    
    def create_customers(self):
        self.stdout.write('Creating customers...')
        
        # Get dealers (or create them if they don't exist)
        try:
            tech_solutions = Dealer.objects.get(code='TECH001')
            smart_systems = Dealer.objects.get(code='SMART002')
            connected_devices = Dealer.objects.get(code='CONN003')
            elite_electronics = Dealer.objects.get(code='ELITE004')
            value_tech = Dealer.objects.get(code='VALUE005')
        except Dealer.DoesNotExist:
            self.stdout.write(self.style.WARNING(
                'Dealers not found. Please run the seed_dealers_data command first, '
                'or uncomment the dealer creation code in this script.'
            ))
            # You could create dealers here as a fallback if needed
            return
        
        # Create corporate customers
        Customer.objects.create(
            name='Acme Corporation',
            customer_type=CustomerType.CORPORATE,
            contact_person='Kemal Yildirim',
            email='kemal@acmecorp.com',
            phone='(555) 111-2222',
            address='234 Corporate Plaza, Istanbul, Turkey',
            tax_id='7890123456',
            tax_office='Istanbul Tax Office',
            dealer=tech_solutions,
            notes='Large account with multiple smart home installations'
        )
        
        Customer.objects.create(
            name='Global Industries Ltd.',
            customer_type=CustomerType.CORPORATE,
            contact_person='Zeynep Kaya',
            email='zeynep@globalind.com',
            phone='(555) 333-4444',
            address='567 Industry Avenue, Ankara, Turkey',
            tax_id='8901234567',
            tax_office='Ankara Corporate Tax Office',
            dealer=smart_systems,
            notes='Medium-sized business focusing on office automation'
        )
        
        Customer.objects.create(
            name='TechStart Innovations',
            customer_type=CustomerType.CORPORATE,
            contact_person='Emre Can',
            email='emre@techstart.com',
            phone='(555) 555-6666',
            address='789 Innovation Park, Izmir, Turkey',
            tax_id='9012345678',
            tax_office='Izmir Tax Office',
            dealer=connected_devices,
            notes='Tech startup with growing smart device needs'
        )
        
        # Create individual customers
        Customer.objects.create(
            name='Ali Yilmaz',
            customer_type=CustomerType.INDIVIDUAL,
            email='ali.yilmaz@example.com',
            phone='(555) 777-8888',
            address='123 Residential St, Apt 45, Istanbul, Turkey',
            dealer=elite_electronics,
            notes='Smart home enthusiast, premium customer'
        )
        
        Customer.objects.create(
            name='Ayşe Demir',
            customer_type=CustomerType.INDIVIDUAL,
            email='ayse.demir@example.com',
            phone='(555) 999-0000',
            address='456 Family Avenue, Antalya, Turkey',
            dealer=tech_solutions,
            notes='New customer interested in security systems'
        )
        
        Customer.objects.create(
            name='Mehmet Öz',
            customer_type=CustomerType.INDIVIDUAL,
            email='mehmet.oz@example.com',
            phone='(555) 123-3456',
            address='789 Urban Street, Ankara, Turkey',
            dealer=value_tech,
            notes='Regular customer, multiple purchases'
        )
        
        Customer.objects.create(
            name='Zehra Akin',
            customer_type=CustomerType.INDIVIDUAL,
            email='zehra.akin@example.com',
            phone='(555) 345-6789',
            address='101 Seaside Road, Izmir, Turkey',
            dealer=connected_devices,
            notes='Interested in energy-saving smart devices'
        )
        
        self.stdout.write(self.style.SUCCESS('Customers created successfully!'))
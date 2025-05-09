from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.inventory.models import (
    Category, Item, Recipe, RecipeItem, Production, ProductionItem,
    ProductionProcess, ProcessItemInput, ProcessItemOutput, PurchaseOrderLine
)
from apps.projects.models import Project

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample inventory data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting inventory data seeding...'))
        
        try:
            with transaction.atomic():
                self.create_categories()
                self.create_items()
                self.create_recipes()
                self.create_productions()
                self.create_production_processes()
                self.create_purchase_order_lines()
                
            self.stdout.write(self.style.SUCCESS('Successfully seeded inventory data!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding data: {str(e)}'))
    
    def create_categories(self):
        self.stdout.write('Creating categories...')
        
        # Create main categories
        raw_materials = Category.objects.create(
            name='Raw Materials',
            description='Raw materials used in production'
        )
        
        components = Category.objects.create(
            name='Components',
            description='Components and parts used in assembly'
        )
        
        finished_products = Category.objects.create(
            name='Finished Products',
            description='Complete products ready for sale'
        )
        
        # Create subcategories
        # Raw Materials subcategories
        Category.objects.create(
            name='Metals',
            description='Metal raw materials',
            parent_category=raw_materials
        )
        
        Category.objects.create(
            name='Plastics',
            description='Plastic raw materials',
            parent_category=raw_materials
        )
        
        electronics = Category.objects.create(
            name='Electronics',
            description='Electronic components',
            parent_category=components
        )
        
        mechanical = Category.objects.create(
            name='Mechanical',
            description='Mechanical components',
            parent_category=components
        )
        
        # Electronics subcategories
        Category.objects.create(
            name='Sensors',
            description='Various types of sensors',
            parent_category=electronics
        )
        
        Category.objects.create(
            name='Circuit Boards',
            description='PCBs and other circuit boards',
            parent_category=electronics
        )
        
        self.stdout.write(self.style.SUCCESS('Categories created successfully!'))
    
    def create_items(self):
        self.stdout.write('Creating items...')
        
        # Get categories
        metals = Category.objects.get(name='Metals')
        plastics = Category.objects.get(name='Plastics')
        sensors = Category.objects.get(name='Sensors')
        circuit_boards = Category.objects.get(name='Circuit Boards')
        mechanical = Category.objects.get(name='Mechanical')
        finished_products = Category.objects.get(name='Finished Products')
        
        # Create raw materials
        aluminum = Item.objects.create(
            name='Aluminum Sheet',
            sku='RAW-AL-001',
            description='Standard aluminum sheet, 1mm thickness',
            item_type='RAW',
            category=metals,
            unit_of_measure='sheet',
            purchase_price=15.50,
            selling_price=0.00  # Raw materials aren't sold directly
        )
        
        steel = Item.objects.create(
            name='Steel Rod',
            sku='RAW-ST-001',
            description='Steel rod, 10mm diameter',
            item_type='RAW',
            category=metals,
            unit_of_measure='meter',
            purchase_price=8.25,
            selling_price=0.00
        )
        
        plastic_granules = Item.objects.create(
            name='ABS Plastic Granules',
            sku='RAW-PL-001',
            description='ABS plastic granules for injection molding',
            item_type='RAW',
            category=plastics,
            unit_of_measure='kg',
            purchase_price=5.00,
            selling_price=0.00
        )
        
        # Create components (intermediate products)
        temp_sensor = Item.objects.create(
            name='Temperature Sensor',
            sku='CMP-SN-001',
            description='Temperature sensor, -50°C to 150°C range',
            item_type='INTERMEDIATE',
            category=sensors,
            unit_of_measure='piece',
            purchase_price=3.50,
            selling_price=7.00
        )
        
        pressure_sensor = Item.objects.create(
            name='Pressure Sensor',
            sku='CMP-SN-002',
            description='Pressure sensor, 0-10 bar range',
            item_type='INTERMEDIATE',
            category=sensors,
            unit_of_measure='piece',
            purchase_price=4.75,
            selling_price=9.50
        )
        
        main_board = Item.objects.create(
            name='Main Control Board',
            sku='CMP-CB-001',
            description='Main control PCB for device control',
            item_type='INTERMEDIATE',
            category=circuit_boards,
            unit_of_measure='piece',
            purchase_price=12.00,
            selling_price=24.00
        )
        
        enclosure = Item.objects.create(
            name='Plastic Enclosure',
            sku='CMP-MC-001',
            description='Plastic enclosure for electronic devices',
            item_type='INTERMEDIATE',
            category=mechanical,
            unit_of_measure='piece',
            purchase_price=7.00,
            selling_price=14.00
        )
        
        # Create finished products
        smart_thermostat = Item.objects.create(
            name='Smart Thermostat',
            sku='PRD-TH-001',
            description='Smart thermostat with WiFi connectivity',
            item_type='FINAL',
            category=finished_products,
            unit_of_measure='piece',
            purchase_price=35.00,
            selling_price=89.99
        )
        
        pressure_controller = Item.objects.create(
            name='Industrial Pressure Controller',
            sku='PRD-PC-001',
            description='Industrial pressure control and monitoring device',
            item_type='FINAL',
            category=finished_products,
            unit_of_measure='piece',
            purchase_price=45.00,
            selling_price=129.99
        )
        
        self.stdout.write(self.style.SUCCESS('Items created successfully!'))
    
    def create_recipes(self):
        self.stdout.write('Creating manufacturing recipes...')
        
        # Get components and products
        temp_sensor = Item.objects.get(sku='CMP-SN-001')
        pressure_sensor = Item.objects.get(sku='CMP-SN-002')
        main_board = Item.objects.get(sku='CMP-CB-001')
        enclosure = Item.objects.get(sku='CMP-MC-001')
        aluminum = Item.objects.get(sku='RAW-AL-001')
        steel = Item.objects.get(sku='RAW-ST-001')
        plastic_granules = Item.objects.get(sku='RAW-PL-001')
        smart_thermostat = Item.objects.get(sku='PRD-TH-001')
        pressure_controller = Item.objects.get(sku='PRD-PC-001')
        
        # Create Recipe for enclosure
        enclosure_recipe = Recipe.objects.create(
            name='Enclosure Manufacturing',
            description='Recipe for manufacturing the device enclosure',
            output_item=enclosure,
            output_quantity=1.0,
            unit_of_measure='piece',
            active=True
        )
        
        # Add inputs to enclosure recipe
        RecipeItem.objects.create(
            recipe=enclosure_recipe,
            input_item=plastic_granules,
            quantity_required=0.5,
            unit_of_measure='kg',
            sequence=10,
            is_optional=False
        )
        
        # Create Recipe for main board
        mainboard_recipe = Recipe.objects.create(
            name='Main Board Assembly',
            description='Recipe for assembling the main circuit board',
            output_item=main_board,
            output_quantity=1.0,
            unit_of_measure='piece',
            active=True
        )
        
        # Add inputs to main board recipe
        RecipeItem.objects.create(
            recipe=mainboard_recipe,
            input_item=aluminum,
            quantity_required=0.1,
            unit_of_measure='sheet',
            sequence=10,
            is_optional=False
        )
        
        # Create Recipe for smart thermostat
        thermostat_recipe = Recipe.objects.create(
            name='Smart Thermostat Assembly',
            description='Recipe for assembling the smart thermostat product',
            output_item=smart_thermostat,
            output_quantity=1.0,
            unit_of_measure='piece',
            active=True
        )
        
        # Add inputs to thermostat recipe
        RecipeItem.objects.create(
            recipe=thermostat_recipe,
            input_item=temp_sensor,
            quantity_required=1,
            unit_of_measure='piece',
            sequence=10,
            is_optional=False
        )
        
        RecipeItem.objects.create(
            recipe=thermostat_recipe,
            input_item=main_board,
            quantity_required=1,
            unit_of_measure='piece',
            sequence=20,
            is_optional=False
        )
        
        RecipeItem.objects.create(
            recipe=thermostat_recipe,
            input_item=enclosure,
            quantity_required=1,
            unit_of_measure='piece',
            sequence=30,
            is_optional=False
        )
        
        # Create Recipe for pressure controller
        pressure_recipe = Recipe.objects.create(
            name='Pressure Controller Assembly',
            description='Recipe for assembling the pressure controller product',
            output_item=pressure_controller,
            output_quantity=1.0,
            unit_of_measure='piece',
            active=True
        )
        
        # Add inputs to pressure controller recipe
        RecipeItem.objects.create(
            recipe=pressure_recipe,
            input_item=pressure_sensor,
            quantity_required=1,
            unit_of_measure='piece',
            sequence=10,
            is_optional=False
        )
        
        RecipeItem.objects.create(
            recipe=pressure_recipe,
            input_item=main_board,
            quantity_required=1,
            unit_of_measure='piece',
            sequence=20,
            is_optional=False
        )
        
        RecipeItem.objects.create(
            recipe=pressure_recipe,
            input_item=enclosure,
            quantity_required=1,
            unit_of_measure='piece',
            sequence=30,
            is_optional=False
        )
        
        RecipeItem.objects.create(
            recipe=pressure_recipe,
            input_item=steel,
            quantity_required=0.2,
            unit_of_measure='meter',
            sequence=40,
            is_optional=False
        )
        
        self.stdout.write(self.style.SUCCESS('Manufacturing recipes created successfully!'))
    
    def create_productions(self):
        self.stdout.write('Creating production records...')
        
        # Get recipes and user
        thermostat_recipe = Recipe.objects.get(name='Smart Thermostat Assembly')
        enclosure_recipe = Recipe.objects.get(name='Enclosure Manufacturing')
        admin_user = User.objects.get(username='admin')
        
        # Create production record for smart thermostat production
        thermostat_production = Production.objects.create(
            recipe=thermostat_recipe,
            output_quantity=Decimal('5.0'),  # Produced 5 units
            executed_by=admin_user,
            notes='Initial production batch of smart thermostats'
        )
        
        # Record consumed items based on recipe
        for recipe_item in thermostat_recipe.items.all():
            ProductionItem.objects.create(
                production=thermostat_production,
                input_item=recipe_item.input_item,
                quantity_consumed=recipe_item.quantity_required * Decimal('5.0'),  # 5 times the recipe quantity
                unit_of_measure=recipe_item.unit_of_measure
            )
        
        # Create production record for enclosures
        enclosure_production = Production.objects.create(
            recipe=enclosure_recipe,
            output_quantity=Decimal('10.0'),  # Produced 10 units
            executed_by=admin_user,
            notes='Enclosure manufacturing batch'
        )
        
        # Record consumed items based on recipe
        for recipe_item in enclosure_recipe.items.all():
            ProductionItem.objects.create(
                production=enclosure_production,
                input_item=recipe_item.input_item,
                quantity_consumed=recipe_item.quantity_required * Decimal('10.0'),  # 10 times the recipe quantity
                unit_of_measure=recipe_item.unit_of_measure
            )
        
        self.stdout.write(self.style.SUCCESS('Production records created successfully!'))
    
    def create_production_processes(self):
        self.stdout.write('Creating production processes...')
        
        # Get products and components
        smart_thermostat = Item.objects.get(sku='PRD-TH-001')
        temp_sensor = Item.objects.get(sku='CMP-SN-001')
        main_board = Item.objects.get(sku='CMP-CB-001')
        enclosure = Item.objects.get(sku='CMP-MC-001')
        
        # Get or create a project
        try:
            project = Project.objects.first()
            if not project:
                # Check if there are any users
                user = User.objects.first()
                if not user:
                    user = User.objects.create_user(
                        username='admin',
                        email='admin@example.com',
                        password='admin123'
                    )
                
                project = Project.objects.create(
                    name='Smart Home Devices',
                    description='Development and production of smart home devices',
                    status='ACTIVE',
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date() + timezone.timedelta(days=365),
                    owner=user
                )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error getting/creating project: {str(e)}'))
            return
        
        # Create production process
        process = ProductionProcess.objects.create(
            project=project,
            name='Smart Thermostat Production Batch #1',
            description='First production batch of smart thermostats',
            process_start_date=timezone.now() - timezone.timedelta(days=5),
            process_end_date=timezone.now() - timezone.timedelta(days=2),
            performed_by=User.objects.first(),
            status='COMPLETED',
            target_output_item=smart_thermostat,
            target_output_quantity=100
        )
        
        # Create process inputs (consumed items)
        ProcessItemInput.objects.create(
            process=process,
            item=temp_sensor,
            quantity_consumed=105  # Extra 5 units for potential defects
        )
        
        ProcessItemInput.objects.create(
            process=process,
            item=main_board,
            quantity_consumed=102
        )
        
        ProcessItemInput.objects.create(
            process=process,
            item=enclosure,
            quantity_consumed=101
        )
        
        # Create process outputs (produced items)
        ProcessItemOutput.objects.create(
            process=process,
            item=smart_thermostat,
            quantity_produced=98  # Some units failed quality control
        )
        
        # Create another production process (in progress)
        process2 = ProductionProcess.objects.create(
            project=project,
            name='Smart Thermostat Production Batch #2',
            description='Second production batch of smart thermostats',
            process_start_date=timezone.now() - timezone.timedelta(days=1),
            performed_by=User.objects.first(),
            status='IN_PROGRESS',
            target_output_item=smart_thermostat,
            target_output_quantity=200
        )
        
        # Create inputs for the in-progress batch
        ProcessItemInput.objects.create(
            process=process2,
            item=temp_sensor,
            quantity_consumed=150  # Partially consumed so far
        )
        
        ProcessItemInput.objects.create(
            process=process2,
            item=main_board,
            quantity_consumed=120
        )
        
        ProcessItemInput.objects.create(
            process=process2,
            item=enclosure,
            quantity_consumed=100
        )
        
        # Create partial outputs for the in-progress batch
        ProcessItemOutput.objects.create(
            process=process2,
            item=smart_thermostat,
            quantity_produced=90  # Production still in progress
        )
        
        self.stdout.write(self.style.SUCCESS('Production processes created successfully!'))
    
    def create_purchase_order_lines(self):
        self.stdout.write('Creating purchase order lines...')
        
        # Get raw materials and components that would be purchased
        aluminum = Item.objects.get(sku='RAW-AL-001')
        steel = Item.objects.get(sku='RAW-ST-001')
        plastic_granules = Item.objects.get(sku='RAW-PL-001')
        temp_sensor = Item.objects.get(sku='CMP-SN-001')
        pressure_sensor = Item.objects.get(sku='CMP-SN-002')
        
        # Create purchase order lines (assuming purchase orders would be in another app)
        purchase_order_id = '550e8400-e29b-41d4-a716-446655440000'  # Example UUID
        
        PurchaseOrderLine.objects.create(
            purchase_order_id=purchase_order_id,
            item=aluminum,
            quantity=50,
            unit_price=15.50
        )
        
        PurchaseOrderLine.objects.create(
            purchase_order_id=purchase_order_id,
            item=steel,
            quantity=100,
            unit_price=8.25
        )
        
        PurchaseOrderLine.objects.create(
            purchase_order_id=purchase_order_id,
            item=plastic_granules,
            quantity=200,
            unit_price=5.00
        )
        
        # Create another purchase order
        purchase_order_id2 = '660e8400-e29b-41d4-a716-446655440001'  # Example UUID
        
        PurchaseOrderLine.objects.create(
            purchase_order_id=purchase_order_id2,
            item=temp_sensor,
            quantity=500,
            unit_price=3.50
        )
        
        PurchaseOrderLine.objects.create(
            purchase_order_id=purchase_order_id2,
            item=pressure_sensor,
            quantity=300,
            unit_price=4.75
        )
        
        self.stdout.write(self.style.SUCCESS('Purchase order lines created successfully!'))

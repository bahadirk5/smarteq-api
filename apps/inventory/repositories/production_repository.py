from django.db.models import Prefetch, Q
from apps.inventory.models.production import Production
from apps.inventory.models.production_item import ProductionItem
from apps.inventory.models.production_history import ProductionHistory


class ProductionRepository:
    """Repository for Production model database operations"""
    
    @staticmethod
    def get_all_productions(filters=None):
        """Get all production records with optional filtering"""
        queryset = Production.objects.all()
        
        if filters:
            # Apply filters if provided
            if 'recipe_id' in filters:
                queryset = queryset.filter(recipe_id=filters['recipe_id'])
            if 'executed_by_id' in filters:
                queryset = queryset.filter(executed_by_id=filters['executed_by_id'])
            if 'date_from' in filters and filters['date_from']:
                queryset = queryset.filter(execution_date__gte=filters['date_from'])
            if 'date_to' in filters and filters['date_to']:
                queryset = queryset.filter(execution_date__lte=filters['date_to'])
        
        # Optimize with select_related and prefetch_related to avoid N+1 queries
        return queryset.select_related('recipe', 'recipe__output_item', 'executed_by').prefetch_related(
            Prefetch(
                'consumed_items',
                queryset=ProductionItem.objects.select_related('input_item')
            )
        )
    
    @staticmethod
    def get_production_by_id(production_id):
        """Get a specific production record by ID with all related data"""
        try:
            return Production.objects.select_related('recipe', 'recipe__output_item', 'executed_by').prefetch_related(
                Prefetch(
                    'consumed_items',
                    queryset=ProductionItem.objects.select_related('input_item')
                ),
                Prefetch(
                    'history',
                    queryset=ProductionHistory.objects.select_related('performed_by').order_by('-timestamp')
                )
            ).get(id=production_id)
        except Production.DoesNotExist:
            return None
    
    @staticmethod
    def create_production(production_data):
        """Create a new production record"""
        return Production.objects.create(**production_data)
    
    @staticmethod
    def update_production(production, production_data):
        """Update an existing production record"""
        for key, value in production_data.items():
            setattr(production, key, value)
        production.save()
        return production
    
    @staticmethod
    def delete_production(production):
        """Delete a production record"""
        production.delete()
    
    @staticmethod
    def add_production_item(production_item_data):
        """Add a consumed item to a production record"""
        return ProductionItem.objects.create(**production_item_data)
    
    @staticmethod
    def update_production_item(production_item, production_item_data):
        """Update a production item"""
        for key, value in production_item_data.items():
            setattr(production_item, key, value)
        production_item.save()
        return production_item
    
    @staticmethod
    def delete_production_item(production_item):
        """Delete a production item"""
        production_item.delete()
    
    @staticmethod
    def get_production_item_by_id(production_item_id):
        """Get a specific production item by ID"""
        try:
            return ProductionItem.objects.select_related('production', 'input_item').get(id=production_item_id)
        except ProductionItem.DoesNotExist:
            return None
    
    @staticmethod
    def get_production_items(production_id):
        """Get all consumed items for a specific production"""
        return ProductionItem.objects.filter(production_id=production_id).select_related('input_item')
    
    @staticmethod
    def add_production_history(history_data):
        """Add a history record for a production event"""
        return ProductionHistory.objects.create(**history_data)
    
    @staticmethod
    def get_production_history(production_id):
        """Get all history records for a specific production"""
        return ProductionHistory.objects.filter(production_id=production_id).select_related('performed_by').order_by('-timestamp')

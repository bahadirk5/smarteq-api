from django.db.models import Prefetch, Q
from apps.inventory.models.recipe import Recipe
from apps.inventory.models.recipe_item import RecipeItem


class RecipeRepository:
    """Repository for Recipe model database operations"""
    
    @staticmethod
    def get_all_recipes(filters=None):
        """Get all recipes with optional filtering"""
        queryset = Recipe.objects.all()
        
        if filters:
            # Apply filters if provided
            if 'name' in filters:
                queryset = queryset.filter(name__icontains=filters['name'])
            if 'output_item_id' in filters:
                queryset = queryset.filter(output_item_id=filters['output_item_id'])
            if 'active' in filters:
                queryset = queryset.filter(active=filters['active'])
        
        # Optimize with select_related and prefetch_related to avoid N+1 queries
        return queryset.select_related('output_item').prefetch_related(
            Prefetch(
                'items',
                queryset=RecipeItem.objects.select_related('input_item').order_by('sequence')
            )
        )
    
    @staticmethod
    def get_recipe_by_id(recipe_id):
        """Get a specific recipe by ID with all related data"""
        try:
            return Recipe.objects.select_related('output_item').prefetch_related(
                Prefetch(
                    'items',
                    queryset=RecipeItem.objects.select_related('input_item').order_by('sequence')
                )
            ).get(id=recipe_id)
        except Recipe.DoesNotExist:
            return None
    
    @staticmethod
    def create_recipe(recipe_data):
        """Create a new recipe"""
        return Recipe.objects.create(**recipe_data)
    
    @staticmethod
    def update_recipe(recipe, recipe_data):
        """Update an existing recipe"""
        for key, value in recipe_data.items():
            setattr(recipe, key, value)
        recipe.save()
        return recipe
    
    @staticmethod
    def delete_recipe(recipe):
        """Delete a recipe"""
        recipe.delete()
        
    @staticmethod
    def add_recipe_item(recipe_item_data):
        """Add an item to a recipe"""
        return RecipeItem.objects.create(**recipe_item_data)
    
    @staticmethod
    def update_recipe_item(recipe_item, recipe_item_data):
        """Update a recipe item"""
        for key, value in recipe_item_data.items():
            setattr(recipe_item, key, value)
        recipe_item.save()
        return recipe_item
    
    @staticmethod
    def delete_recipe_item(recipe_item):
        """Delete a recipe item"""
        recipe_item.delete()
    
    @staticmethod
    def get_recipe_item_by_id(recipe_item_id):
        """Get a specific recipe item by ID"""
        try:
            return RecipeItem.objects.select_related('recipe', 'input_item').get(id=recipe_item_id)
        except RecipeItem.DoesNotExist:
            return None
    
    @staticmethod
    def get_recipe_items(recipe_id):
        """Get all items for a specific recipe"""
        return RecipeItem.objects.filter(recipe_id=recipe_id).select_related('input_item').order_by('sequence')

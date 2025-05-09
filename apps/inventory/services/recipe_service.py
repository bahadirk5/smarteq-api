from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from apps.common.responses import success_response, error_response
from apps.inventory.repositories.recipe_repository import RecipeRepository
from apps.inventory.repositories.item_repository import ItemRepository


class RecipeService:
    """Service class for Recipe-related operations"""
    
    def __init__(self):
        self.recipe_repository = RecipeRepository()
        self.item_repository = ItemRepository()
    
    def get_all_recipes(self, filters=None):
        """Get all recipes with optional filtering"""
        try:
            recipes = self.recipe_repository.get_all_recipes(filters)
            return success_response(data=recipes)
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_recipe_by_id(self, recipe_id):
        """Get a specific recipe by ID"""
        try:
            recipe = self.recipe_repository.get_recipe_by_id(recipe_id)
            if not recipe:
                return error_response(_('Recipe not found'), status_code=status.HTTP_404_NOT_FOUND)
            return success_response(data=recipe)
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def create_recipe(self, recipe_data, recipe_items_data=None):
        """Create a new recipe with optional recipe items"""
        try:
            # Debug logging
            print(f"Creating recipe with data: {recipe_data}")
            print(f"Recipe items data: {recipe_items_data}")
            
            # Don't make a copy of recipe_data - we need to preserve the actual Item objects
            
            # Verify output item exists - handle if it's an object instead of just an ID
            output_item = recipe_data.get('output_item')
            
            # If output_item is an ID (UUID string), fetch the actual Item object
            if isinstance(output_item, str):
                output_item_obj = self.item_repository.get_item_by_id(output_item)
                if not output_item_obj:
                    return error_response(_('Output item not found'), status_code=status.HTTP_400_BAD_REQUEST)
                recipe_data['output_item'] = output_item_obj
                output_item_id = output_item
            else:
                # It's already an Item object
                output_item_id = output_item.id
            
            # Create the recipe
            recipe = self.recipe_repository.create_recipe(recipe_data)
            
            # Add recipe items if provided
            if recipe_items_data:
                for item_data in recipe_items_data:
                    # Create a new dict to avoid modifying the original
                    recipe_item = item_data.copy()
                    recipe_item['recipe'] = recipe
                    
                    # Verify input item exists - handle either object, ID string, or dict
                    input_item = item_data.get('input_item')
                    
                    # If input_item is a string (UUID), get the actual Item object
                    if isinstance(input_item, str):
                        input_item_obj = self.item_repository.get_item_by_id(input_item)
                        if not input_item_obj:
                            # Rollback transaction and return error
                            transaction.set_rollback(True)
                            return error_response(_('Input item not found'), status_code=status.HTTP_400_BAD_REQUEST)
                        recipe_item['input_item'] = input_item_obj
                        input_item_id = input_item
                    # If input_item is a dictionary, extract the ID
                    elif isinstance(input_item, dict) and 'id' in input_item:
                        input_item_id = input_item['id']
                        input_item_obj = self.item_repository.get_item_by_id(input_item_id)
                        if not input_item_obj:
                            transaction.set_rollback(True)
                            return error_response(_('Input item not found'), status_code=status.HTTP_400_BAD_REQUEST)
                        recipe_item['input_item'] = input_item_obj
                    # If input_item is already an Item object
                    elif hasattr(input_item, 'id'):
                        input_item_id = input_item.id
                    else:
                        transaction.set_rollback(True)
                        return error_response(_('Invalid input_item format'), status_code=status.HTTP_400_BAD_REQUEST)
                    
                    # Prevent circular references (output = input)
                    if str(input_item_id) == str(output_item_id):
                        transaction.set_rollback(True)
                        return error_response(_('A recipe cannot use its own output item as an ingredient'), 
                                             status_code=status.HTTP_400_BAD_REQUEST)
                    
                    self.recipe_repository.add_recipe_item(recipe_item)
            
            # Get fresh data with all relationships
            recipe = self.recipe_repository.get_recipe_by_id(recipe.id)
            return success_response(data=recipe, status_code=status.HTTP_201_CREATED)
        except Exception as e:
            # Enhanced error logging
            import traceback
            print(f"Error in create_recipe: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            transaction.set_rollback(True)
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def update_recipe(self, recipe_id, recipe_data):
        """Update an existing recipe"""
        try:
            recipe = self.recipe_repository.get_recipe_by_id(recipe_id)
            if not recipe:
                return error_response(_('Recipe not found'), status_code=status.HTTP_404_NOT_FOUND)
            
            # If changing output item, verify it exists
            if 'output_item' in recipe_data:
                output_item_id = recipe_data.get('output_item')
                if not self.item_repository.get_item_by_id(output_item_id):
                    return error_response(_('Output item not found'), status_code=status.HTTP_400_BAD_REQUEST)
            
            updated_recipe = self.recipe_repository.update_recipe(recipe, recipe_data)
            return success_response(data=updated_recipe)
        except Exception as e:
            transaction.set_rollback(True)
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete_recipe(self, recipe_id):
        """Delete a recipe"""
        try:
            recipe = self.recipe_repository.get_recipe_by_id(recipe_id)
            if not recipe:
                return error_response(_('Recipe not found'), status_code=status.HTTP_404_NOT_FOUND)
            
            # Check if there are any productions using this recipe
            # (This would be implemented in the Production repository/service)
            # if has_related_productions:
            #    return error_response(_('Cannot delete recipe with related productions'), 
            #                          status_code=status.HTTP_400_BAD_REQUEST)
            
            self.recipe_repository.delete_recipe(recipe)
            return success_response(message=_('Recipe deleted successfully'))
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Recipe Item operations
    
    @transaction.atomic
    def add_recipe_item(self, recipe_id, item_data):
        """Add an item to a recipe"""
        try:
            recipe = self.recipe_repository.get_recipe_by_id(recipe_id)
            if not recipe:
                return error_response(_('Recipe not found'), status_code=status.HTTP_404_NOT_FOUND)
            
            # Verify input item exists
            input_item_id = item_data.get('input_item')
            if not self.item_repository.get_item_by_id(input_item_id):
                return error_response(_('Input item not found'), status_code=status.HTTP_400_BAD_REQUEST)
            
            # Prevent circular references
            if str(input_item_id) == str(recipe.output_item.id):
                return error_response(_('A recipe cannot use its own output item as an ingredient'), 
                                     status_code=status.HTTP_400_BAD_REQUEST)
            
            # Add recipe to item data
            item_data['recipe'] = recipe
            
            recipe_item = self.recipe_repository.add_recipe_item(item_data)
            return success_response(data=recipe_item, status_code=status.HTTP_201_CREATED)
        except Exception as e:
            transaction.set_rollback(True)
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update_recipe_item(self, recipe_item_id, item_data):
        """Update a recipe item"""
        try:
            recipe_item = self.recipe_repository.get_recipe_item_by_id(recipe_item_id)
            if not recipe_item:
                return error_response(_('Recipe item not found'), status_code=status.HTTP_404_NOT_FOUND)
            
            # If changing input item, verify it exists and check for circular references
            if 'input_item' in item_data:
                input_item_id = item_data.get('input_item')
                if not self.item_repository.get_item_by_id(input_item_id):
                    return error_response(_('Input item not found'), status_code=status.HTTP_400_BAD_REQUEST)
                
                if str(input_item_id) == str(recipe_item.recipe.output_item.id):
                    return error_response(_('A recipe cannot use its own output item as an ingredient'), 
                                         status_code=status.HTTP_400_BAD_REQUEST)
            
            updated_item = self.recipe_repository.update_recipe_item(recipe_item, item_data)
            return success_response(data=updated_item)
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete_recipe_item(self, recipe_item_id):
        """Delete a recipe item"""
        try:
            recipe_item = self.recipe_repository.get_recipe_item_by_id(recipe_item_id)
            if not recipe_item:
                return error_response(_('Recipe item not found'), status_code=status.HTTP_404_NOT_FOUND)
            
            self.recipe_repository.delete_recipe_item(recipe_item)
            return success_response(message=_('Recipe item deleted successfully'))
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_recipe_items(self, recipe_id):
        """Get all items for a specific recipe"""
        try:
            recipe = self.recipe_repository.get_recipe_by_id(recipe_id)
            if not recipe:
                return error_response(_('Recipe not found'), status_code=status.HTTP_404_NOT_FOUND)
            
            recipe_items = self.recipe_repository.get_recipe_items(recipe_id)
            return success_response(data=recipe_items)
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import status
import traceback
import logging
import uuid

from apps.common.responses import success_response, error_response
from apps.inventory.repositories.production_repository import ProductionRepository
from apps.inventory.repositories.recipe_repository import RecipeRepository
from apps.inventory.repositories.item_repository import ItemRepository
from apps.inventory.repositories.inventory_repository import InventoryRepository
from apps.inventory.utils.logger import LoggerMixin, log_exception
from apps.inventory.models.recipe import Recipe


class ProductionService(LoggerMixin):
    """Service class for Production-related operations"""
    
    def __init__(self):
        self.production_repository = ProductionRepository()
        self.recipe_repository = RecipeRepository()
        self.item_repository = ItemRepository()
        self.inventory_repository = InventoryRepository()
        self.log_info("ProductionService initialized")
    
    def get_all_productions(self, filters=None):
        """Get all production records with optional filtering"""
        try:
            self.log_debug(f"Getting all productions with filters: {filters}")
            productions = self.production_repository.get_all_productions(filters)
            return success_response(data=productions)
        except Exception as e:
            self.log_exception(f"Error getting productions: {str(e)}")
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_production_by_id(self, production_id):
        """Get a specific production record by ID"""
        try:
            self.log_debug(f"Getting production with ID: {production_id}")
            production = self.production_repository.get_production_by_id(production_id)
            if not production:
                self.log_warning(f"Production with ID {production_id} not found")
                return error_response(_('Production record not found'), status_code=status.HTTP_404_NOT_FOUND)
            return success_response(data=production)
        except Exception as e:
            self.log_exception(f"Error getting production {production_id}: {str(e)}")
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def create_production(self, production_data, user):
        """Create a new production record and process inventory adjustments"""
        try:
            # Log the incoming request data
            self.log_info(f"Creating production with data: {production_data}")
            self.log_debug(f"User executing production: {user.username} (ID: {user.id})")
            
            # Check if user is authenticated
            if not user.is_authenticated:
                error_msg = "User is not authenticated"
                self.log_error(error_msg)
                return error_response(_(error_msg), status_code=status.HTTP_401_UNAUTHORIZED)
            
            # Handle recipe which can be either a UUID or a Recipe object
            recipe = production_data.get('recipe')
            self.log_debug(f"Recipe from request: {recipe}, type: {type(recipe)}")
            
            # If recipe is already a Recipe object
            if isinstance(recipe, Recipe):
                recipe_id = recipe.id
                self.log_debug(f"Recipe is already a Recipe object with ID: {recipe_id}")
            else:
                # Try to convert to UUID if it's a string
                try:
                    recipe_id = uuid.UUID(str(recipe))
                    self.log_debug(f"Converted recipe ID to UUID: {recipe_id}")
                except (ValueError, TypeError, AttributeError) as e:
                    error_msg = f"Invalid recipe ID format: {str(e)}"
                    self.log_error(error_msg)
                    return error_response(_(error_msg), status_code=status.HTTP_400_BAD_REQUEST)
            
            # Now get the recipe with validated UUID
            recipe = self.recipe_repository.get_recipe_by_id(recipe_id)
            if not recipe:
                error_msg = f"Recipe with ID {recipe_id} not found"
                self.log_error(error_msg)
                return error_response(_(error_msg), status_code=status.HTTP_400_BAD_REQUEST)
            
            # Ensure we're using the validated recipe
            production_data['recipe'] = recipe
            
            self.log_debug(f"Recipe found: {recipe.name} (ID: {recipe.id})")
            
            # Add user to production data
            production_data['executed_by'] = user
            
            # If consumed items not provided, use recipe items as default
            consumed_items_data = production_data.pop('consumed_items', None)
            if consumed_items_data is None:
                self.log_debug("Calculating consumed items based on recipe")
                # Calculate quantities based on recipe and output quantity
                output_quantity = production_data.get('output_quantity')
                consumed_items_data = []
                
                # For each recipe item, calculate required quantity
                recipe_items = self.recipe_repository.get_recipe_items(recipe.id)
                self.log_debug(f"Found {len(recipe_items)} items in recipe")
                
                for recipe_item in recipe_items:
                    # Skip optional items that might not be available
                    if recipe_item.is_optional:
                        self.log_debug(f"Skipping optional item: {recipe_item.input_item.name}")
                        continue
                    
                    # Calculate required quantity proportional to output
                    quantity_factor = output_quantity / recipe.output_quantity
                    required_quantity = recipe_item.quantity_required * quantity_factor
                    
                    self.log_debug(f"Adding item {recipe_item.input_item.name} with quantity {required_quantity}")
                    
                    consumed_items_data.append({
                        'input_item': recipe_item.input_item,
                        'quantity_consumed': required_quantity,
                        'unit_of_measure': recipe_item.unit_of_measure
                    })
            
            # Check if we have enough inventory for all consumed items
            self.log_info("Checking inventory levels for consumed items")
            for item_data in consumed_items_data:
                item_id = item_data['input_item'].id if hasattr(item_data['input_item'], 'id') else item_data['input_item']
                quantity = item_data['quantity_consumed']
                
                # Check inventory
                inventory_response = self.inventory_repository.get_item_quantity(item_id)
                available_quantity = inventory_response.get('available_quantity', 0)
                self.log_debug(f"Item ID: {item_id}, Required: {quantity}, Available: {available_quantity}")
                
                if available_quantity < quantity:
                    item = self.item_repository.get_item_by_id(item_id)
                    item_name = item.name if item else f"Item ID: {item_id}"
                    error_msg = f'Insufficient inventory for {item_name}. Required: {quantity}, Available: {available_quantity}'
                    self.log_error(error_msg)
                    return error_response(_(error_msg), status_code=status.HTTP_400_BAD_REQUEST)
            
            # Create production record
            self.log_info("Creating production record")
            production = self.production_repository.create_production(production_data)
            self.log_debug(f"Production record created with ID: {production.id}")
            
            # Add consumed items
            self.log_info("Adding consumed items")
            for item_data in consumed_items_data:
                # Ensure input_item is an Item object, not a UUID or ID
                if not hasattr(item_data['input_item'], 'id'):
                    # We have an ID or UUID, need to get the Item object
                    item_id = item_data['input_item']
                    self.log_debug(f"Converting input_item ID {item_id} to Item object")
                    item = self.item_repository.get_item_by_id(item_id)
                    if not item:
                        error_msg = f"Item with ID {item_id} not found"
                        self.log_error(error_msg)
                        raise ValueError(error_msg)
                    item_data['input_item'] = item

                # Set production reference
                item_data['production'] = production
                self.log_debug(f"Adding consumed item: {item_data}")
                self.production_repository.add_production_item(item_data)
                
                # Get item ID for inventory adjustment
                item_id = item_data['input_item'].id
                
                # Adjust inventory: decrease consumed items
                self.log_debug(f"Adjusting inventory for item ID: {item_id}, quantity: -{item_data['quantity_consumed']}")
                self.inventory_repository.adjust_inventory(
                    item_id=item_id,
                    quantity=-item_data['quantity_consumed'],  # Negative for decrement
                    reason=f"Consumed in Production #{production.id}",
                    reference_id=str(production.id),
                    performed_by=user
                )
            
            # Adjust inventory: increase produced item
            self.log_info(f"Increasing inventory for produced item ID: {recipe.output_item.id}, quantity: {production_data['output_quantity']}")
            self.inventory_repository.adjust_inventory(
                item_id=recipe.output_item.id,
                quantity=production_data['output_quantity'],  # Positive for increment
                reason=f"Created in Production #{production.id}",
                reference_id=str(production.id),
                performed_by=user
            )
            
            # Add production history record
            self.log_info("Adding production history record")
            self.production_repository.add_production_history({
                'production': production,
                'action': 'Created',
                'performed_by': user,
                'notes': 'Production record created',
                'new_data': {
                    'recipe_id': str(recipe_id),
                    'output_quantity': str(production_data['output_quantity']),
                    'consumed_items': len(consumed_items_data)
                }
            })
            
            # Get fresh data with all relationships
            production = self.production_repository.get_production_by_id(production.id)
            self.log_info(f"Production process completed successfully for ID: {production.id}")
            return success_response(data=production, status_code=status.HTTP_201_CREATED)
        except Exception as e:
            # Full exception logging with traceback
            tb = traceback.format_exc()
            self.log_error(f"Exception during production creation: {str(e)}\nTraceback:\n{tb}")
            
            # Ensure transaction rollback
            transaction.set_rollback(True)
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def update_production(self, production_id, production_data, user):
        """Update an existing production record and adjust inventory if needed"""
        try:
            production = self.production_repository.get_production_by_id(production_id)
            if not production:
                return error_response(_('Production record not found'), status_code=status.HTTP_404_NOT_FOUND)
            
            # Store original data for history and inventory adjustments
            original_output_quantity = production.output_quantity
            original_recipe = production.recipe
            original_consumed_items = list(self.production_repository.get_production_items(production_id))
            
            # Handle output quantity change
            output_quantity_changed = False
            new_output_quantity = production_data.get('output_quantity')
            if new_output_quantity is not None and new_output_quantity != original_output_quantity:
                output_quantity_changed = True
                output_quantity_diff = new_output_quantity - original_output_quantity
            
            # Handle consumed items changes
            consumed_items_data = production_data.pop('consumed_items', None)
            consumed_items_changed = consumed_items_data is not None
            
            # Verify we have enough inventory for any new consumption
            if consumed_items_changed or output_quantity_changed:
                # If new consumed items provided, check their inventory
                if consumed_items_changed:
                    for item_data in consumed_items_data:
                        item_id = item_data['input_item']
                        quantity = item_data['quantity_consumed']
                        
                        # For each originally consumed item, we'll return it to inventory,
                        # so we only need to check the additional quantity
                        original_item_quantity = 0
                        for orig_item in original_consumed_items:
                            if str(orig_item.input_item.id) == str(item_id):
                                original_item_quantity = orig_item.quantity_consumed
                                break
                        
                        additional_quantity = quantity - original_item_quantity
                        if additional_quantity > 0:  # Only check if we're consuming more than before
                            inventory_response = self.inventory_repository.get_item_quantity(item_id)
                            if inventory_response.get('available_quantity', 0) < additional_quantity:
                                item = self.item_repository.get_item_by_id(item_id)
                                item_name = item.name if item else f"Item ID: {item_id}"
                                return error_response(
                                    _(f'Insufficient inventory for {item_name}. '
                                      f'Required additional: {additional_quantity}, '
                                      f'Available: {inventory_response.get("available_quantity", 0)}'),
                                    status_code=status.HTTP_400_BAD_REQUEST
                                )
                
                # If output quantity increased, check inventory for any additional consumption
                elif output_quantity_changed and output_quantity_diff > 0:
                    # For recipe-based consumption, calculate additional required quantities
                    recipe_items = self.recipe_repository.get_recipe_items(original_recipe.id)
                    
                    for recipe_item in recipe_items:
                        if recipe_item.is_optional:
                            continue
                            
                        # Calculate additional consumption based on output quantity change
                        quantity_factor = output_quantity_diff / original_recipe.output_quantity
                        additional_quantity = recipe_item.quantity_required * quantity_factor
                        
                        if additional_quantity > 0:
                            inventory_response = self.inventory_repository.get_item_quantity(recipe_item.input_item.id)
                            if inventory_response.get('available_quantity', 0) < additional_quantity:
                                return error_response(
                                    _(f'Insufficient inventory for {recipe_item.input_item.name}. '
                                      f'Required additional: {additional_quantity}, '
                                      f'Available: {inventory_response.get("available_quantity", 0)}'),
                                    status_code=status.HTTP_400_BAD_REQUEST
                                )
            
            # Update the production record
            updated_production = self.production_repository.update_production(production, production_data)
            
            # Process inventory adjustments
            
            # 1. If output quantity changed, adjust produced item inventory
            if output_quantity_changed:
                self.inventory_repository.adjust_inventory(
                    item_id=original_recipe.output_item.id,
                    quantity=output_quantity_diff,  # Can be positive or negative
                    reason=f"Production #{production.id} output quantity updated",
                    reference_id=str(production.id),
                    performed_by=user
                )
            
            # 2. If consumed items changed, process each change
            if consumed_items_changed:
                # First, return all original consumed items to inventory
                for orig_item in original_consumed_items:
                    self.inventory_repository.adjust_inventory(
                        item_id=orig_item.input_item.id,
                        quantity=orig_item.quantity_consumed,  # Positive to add back
                        reason=f"Production #{production.id} update - returning consumed item",
                        reference_id=str(production.id),
                        performed_by=user
                    )
                
                # Delete all existing consumed items
                for orig_item in original_consumed_items:
                    self.production_repository.delete_production_item(orig_item)
                
                # Add new consumed items and decrease inventory
                for item_data in consumed_items_data:
                    item_data['production'] = updated_production
                    self.production_repository.add_production_item(item_data)
                    
                    # Decrease inventory for new consumption
                    self.inventory_repository.adjust_inventory(
                        item_id=item_data['input_item'],
                        quantity=-item_data['quantity_consumed'],  # Negative for decrement
                        reason=f"Production #{production.id} update - new consumption",
                        reference_id=str(production.id),
                        performed_by=user
                    )
            
            # Add production history record
            self.production_repository.add_production_history({
                'production': updated_production,
                'action': 'Updated',
                'performed_by': user,
                'notes': 'Production record updated',
                'previous_data': {
                    'output_quantity': str(original_output_quantity),
                    'consumed_items_changed': consumed_items_changed
                },
                'new_data': {
                    'output_quantity': str(production_data.get('output_quantity', original_output_quantity)),
                    'notes': production_data.get('notes')
                }
            })
            
            # Get fresh data with all relationships
            updated_production = self.production_repository.get_production_by_id(updated_production.id)
            return success_response(data=updated_production)
        except Exception as e:
            transaction.set_rollback(True)
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_production_history(self, production_id):
        """Get history records for a production"""
        try:
            production = self.production_repository.get_production_by_id(production_id)
            if not production:
                return error_response(_('Production record not found'), status_code=status.HTTP_404_NOT_FOUND)
            
            history = self.production_repository.get_production_history(production_id)
            return success_response(data=history)
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

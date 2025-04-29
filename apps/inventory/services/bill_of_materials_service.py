from apps.inventory.repositories.bill_of_materials_repository import BillOfMaterialsRepository
from apps.inventory.repositories.item_repository import ItemRepository


class BillOfMaterialsService:
    """
    Service class to handle business logic for BillOfMaterials operations.
    Uses BillOfMaterialsRepository for data access.
    """
    
    def __init__(self):
        self.repository = BillOfMaterialsRepository()
        self.item_repository = ItemRepository()
    
    def get_all_boms(self):
        """Get all bills of materials"""
        return self.repository.get_all_boms()
    
    def get_bom(self, bom_id):
        """Get a bill of materials by its ID"""
        return self.repository.get_bom_by_id(bom_id)
    
    def get_bom_for_item(self, item_id):
        """Get the complete bill of materials for an item"""
        # Ensure the item exists
        item = self.item_repository.get_item_by_id(item_id)
        
        # Get direct components for this item
        components = self.repository.get_boms_by_output_item(item_id)
        
        return components
    
    def get_recursive_bom(self, item_id):
        """Get a recursive bill of materials for an item, including all levels of components"""
        def get_components(output_id, level=0):
            result = []
            components = self.repository.get_boms_by_output_item(output_id)
            
            for component in components:
                component_data = {
                    'id': component.id,
                    'item_id': component.input_item_id,
                    'item_name': component.input_item.name,
                    'item_sku': component.input_item.sku,
                    'quantity': component.quantity_required,
                    'unit': component.unit_of_measure,
                    'sequence': component.sequence,
                    'level': level,
                    'children': []
                }
                
                # If this component is not a raw material, get its components
                if not component.input_item.is_raw_material:
                    component_data['children'] = get_components(component.input_item_id, level + 1)
                
                result.append(component_data)
            
            return result
        
        # Get the item
        item = self.item_repository.get_item_by_id(item_id)
        
        # Build the recursive structure
        return {
            'item_id': item.id,
            'item_name': item.name,
            'item_sku': item.sku,
            'item_type': item.item_type,
            'components': get_components(item_id)
        }
    
    def create_bom(self, bom_data):
        """Create a new bill of materials entry"""
        # Validate that the output item is not a raw material
        output_item = self.item_repository.get_item_by_id(bom_data['output_item_id'])
        if output_item.is_raw_material:
            raise ValueError("Raw materials cannot be an output item in a BOM")
        
        # Validate that the input and output items are not the same
        if bom_data['output_item_id'] == bom_data['input_item_id']:
            raise ValueError("An item cannot be a component of itself")
        
        # Additional validation could be done here
        return self.repository.create_bom(bom_data)
    
    def update_bom(self, bom_id, bom_data):
        """Update an existing bill of materials entry"""
        # Similar validation as in create_bom could be applied here
        return self.repository.update_bom(bom_id, bom_data)
    
    def delete_bom(self, bom_id):
        """Delete a bill of materials entry"""
        return self.repository.delete_bom(bom_id)
    
    def create_complete_bom(self, output_item_id, components_data):
        """Create a complete bill of materials for an item with multiple components"""
        # Validate the output item
        output_item = self.item_repository.get_item_by_id(output_item_id)
        if output_item.is_raw_material:
            raise ValueError("Raw materials cannot be an output item in a BOM")
        
        # Create the BOM entries
        return self.repository.create_bom_components(output_item_id, components_data)

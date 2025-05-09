from django.db import transaction
from apps.inventory.repositories.item_repository import ItemRepository
from apps.inventory.repositories.recipe_repository import RecipeRepository  # Replaces BillOfMaterialsRepository


class CustomizableProductService:
    """
    Service class for managing customizable products and their recipe configurations
    """
    @staticmethod
    def get_product_bom(item_id):
        """
        Get the bill of materials for a product, grouped by alternative components
        """
        item = ItemRepository.get_by_id(item_id)
        if not item:
            return None, "Product not found"
            
        if not item.is_final_product:
            return None, "Item is not a final product"
            
        # Get all BOM entries for this product
        bom_entries = RecipeRepository.get_by_output_item(item_id)
        
        # Group components by alternative_group
        bom_structure = []
        alternative_groups = {}
        
        for entry in bom_entries:
            if entry.alternative_group:
                if entry.alternative_group not in alternative_groups:
                    alternative_groups[entry.alternative_group] = []
                alternative_groups[entry.alternative_group].append(entry)
            else:
                bom_structure.append({
                    'component': entry,
                    'alternatives': []
                })
        
        # Add alternative groups to structure
        for group_name, entries in alternative_groups.items():
            # Find the default component
            default_component = next((e for e in entries if e.is_default), entries[0])
            
            bom_structure.append({
                'component': default_component,
                'alternatives': [e for e in entries if e != default_component]
            })
        
        # Sort by sequence
        bom_structure.sort(key=lambda x: x['component'].sequence)
        
        return bom_structure, None
    
    @staticmethod
    def customize_product(item_id, component_selections):
        """
        Create a customized variant of a product
        
        component_selections format:
        [
            {
                'group': 'alternative_group_name',
                'component_id': selected_component_id
            },
            ...
        ]
        """
        item = ItemRepository.get_by_id(item_id)
        if not item:
            return None, "Product not found"
            
        if not item.is_final_product:
            return None, "Item is not a final product"
        
        # Get standard recipe components
        bom_entries = RecipeRepository.get_by_output_item(item_id)
        
        # Validate component selections
        if component_selections:
            for selection in component_selections:
                group_name = selection.get('group')
                component_id = selection.get('component_id')
                
                if not group_name or not component_id:
                    return None, "Invalid component selection format"
                
                # Check if selected component exists and belongs to the specified group
                component_exists = False
                for entry in bom_entries:
                    if entry.alternative_group == group_name and entry.input_item.id == component_id:
                        component_exists = True
                        break
                
                if not component_exists:
                    return None, f"Invalid component selection: Component {component_id} not found in group {group_name}"
        
        # Create a customized BOM variant
        customized_structure = []
        used_groups = set()
        
        # First add all non-alternative components and selected alternatives
        for entry in bom_entries:
            # Skip optional components that aren't explicitly selected
            if entry.is_optional and entry.alternative_group:
                selection = next((s for s in component_selections if s.get('group') == entry.alternative_group), None)
                if not selection or int(selection.get('component_id')) != entry.input_item.id:
                    continue
            
            # For components with alternatives, only include selected ones
            if entry.alternative_group:
                # If we've already processed this group, skip
                if entry.alternative_group in used_groups:
                    continue
                
                selection = next((s for s in component_selections if s.get('group') == entry.alternative_group), None)
                if selection:
                    # Use selected component
                    component_id = int(selection.get('component_id'))
                    for alt_entry in bom_entries:
                        if alt_entry.alternative_group == entry.alternative_group and alt_entry.input_item.id == component_id:
                            customized_structure.append(alt_entry)
                            break
                else:
                    # Use default component for this group
                    default_entry = next((e for e in bom_entries if e.alternative_group == entry.alternative_group and e.is_default), None)
                    if default_entry:
                        customized_structure.append(default_entry)
                
                used_groups.add(entry.alternative_group)
            else:
                # Regular component with no alternatives
                customized_structure.append(entry)
        
        return customized_structure, None
    
    @staticmethod
    def calculate_material_requirements(item_id, quantity=1, component_selections=None):
        """
        Calculate the raw material requirements for producing a specified quantity of a product
        """
        # Get the customized BOM structure
        if component_selections:
            bom_structure, error = CustomizableProductService.customize_product(item_id, component_selections)
        else:
            bom_structure, error = CustomizableProductService.get_product_bom(item_id)
            # Flatten to just get the default components
            bom_structure = [item['component'] for item in bom_structure] if bom_structure else []
        
        if error:
            return None, error
        
        # Calculate raw material requirements
        material_requirements = {}
        
        for entry in bom_structure:
            input_item = entry.input_item
            required_quantity = entry.quantity_required * quantity
            
            if input_item.is_raw_material:
                # Raw material - add directly to requirements
                if input_item.id in material_requirements:
                    material_requirements[input_item.id]['quantity'] += required_quantity
                else:
                    material_requirements[input_item.id] = {
                        'item': input_item,
                        'quantity': required_quantity,
                        'unit_of_measure': entry.unit_of_measure,
                        'available_quantity': input_item.quantity,
                    }
            else:
                # Intermediate product - recursively calculate its requirements
                sub_requirements, error = CustomizableProductService.calculate_material_requirements(
                    input_item.id, 
                    quantity=required_quantity
                )
                
                if error:
                    return None, f"Error calculating requirements for {input_item.name}: {error}"
                
                # Merge with main requirements
                for item_id, req in sub_requirements.items():
                    if item_id in material_requirements:
                        material_requirements[item_id]['quantity'] += req['quantity']
                    else:
                        material_requirements[item_id] = req
        
        return material_requirements, None
    
    @staticmethod
    @transaction.atomic
    def produce_product(item_id, quantity=1, component_selections=None):
        """
        Produce a product by consuming its required raw materials
        """
        item = ItemRepository.get_by_id(item_id)
        if not item:
            return None, "Product not found"
            
        if not item.is_final_product and not item.is_intermediate_product:
            return None, "Item is not a product"
        
        # Calculate material requirements
        material_requirements, error = CustomizableProductService.calculate_material_requirements(
            item_id, 
            quantity=quantity,
            component_selections=component_selections
        )
        
        if error:
            return None, error
        
        # Check if we have enough inventory
        missing_materials = []
        for item_id, req in material_requirements.items():
            if req['available_quantity'] < req['quantity']:
                missing_materials.append({
                    'item': req['item'],
                    'required': req['quantity'],
                    'available': req['available_quantity'],
                    'shortage': req['quantity'] - req['available_quantity'],
                })
        
        if missing_materials:
            return None, {
                'error': "Insufficient raw materials",
                'missing_materials': missing_materials
            }
        
        # Consume materials
        for item_id, req in material_requirements.items():
            raw_item = req['item']
            consumed_quantity = req['quantity']
            
            ItemRepository.update(
                item_id=raw_item.id,
                quantity=raw_item.quantity - consumed_quantity
            )
        
        # Increase product quantity
        ItemRepository.update(
            item_id=item.id,
            quantity=item.quantity + quantity
        )
        
        # Return production details
        return {
            'product': item,
            'quantity_produced': quantity,
            'materials_consumed': material_requirements
        }, None

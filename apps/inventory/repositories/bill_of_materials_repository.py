from django.shortcuts import get_object_or_404
from apps.inventory.models import BillOfMaterials


class BillOfMaterialsRepository:
    """
    Repository class for BillOfMaterials data access operations.
    Abstracts all database operations related to BillOfMaterials model.
    """
    
    def get_all_boms(self):
        """Get all bills of materials"""
        return BillOfMaterials.objects.all()
    
    def get_bom_by_id(self, bom_id):
        """Get a specific bill of materials by ID"""
        return get_object_or_404(BillOfMaterials, id=bom_id)
    
    def get_boms_by_output_item(self, output_item_id):
        """Get all BOMs where the specified item is the output"""
        return BillOfMaterials.objects.filter(output_item_id=output_item_id).order_by('sequence')
    
    def get_boms_by_input_item(self, input_item_id):
        """Get all BOMs where the specified item is used as an input"""
        return BillOfMaterials.objects.filter(input_item_id=input_item_id)
    
    def create_bom(self, bom_data):
        """Create a new bill of materials entry"""
        return BillOfMaterials.objects.create(**bom_data)
    
    def update_bom(self, bom_id, bom_data):
        """Update an existing bill of materials entry"""
        bom = self.get_bom_by_id(bom_id)
        
        for key, value in bom_data.items():
            setattr(bom, key, value)
        
        bom.save()
        return bom
    
    def delete_bom(self, bom_id):
        """Delete a bill of materials entry"""
        bom = self.get_bom_by_id(bom_id)
        bom.delete()
        return True
    
    def create_bom_components(self, output_item_id, components_data):
        """Create multiple BOM components in a single transaction"""
        bom_entries = []
        
        for component_data in components_data:
            component_data['output_item_id'] = output_item_id
            bom_entry = BillOfMaterials.objects.create(**component_data)
            bom_entries.append(bom_entry)
            
        return bom_entries

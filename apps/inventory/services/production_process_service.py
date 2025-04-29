from django.db import transaction
from apps.inventory.repositories.production_process_repository import ProductionProcessRepository
from apps.inventory.repositories.item_repository import ItemRepository
from apps.inventory.repositories.bill_of_materials_repository import BillOfMaterialsRepository


class ProductionProcessService:
    """
    Service class to handle business logic for Production Process operations.
    Uses ProductionProcessRepository, ItemRepository and BillOfMaterialsRepository for data access.
    """
    
    def __init__(self):
        self.repository = ProductionProcessRepository()
        self.item_repository = ItemRepository()
        self.bom_repository = BillOfMaterialsRepository()
    
    def get_all_processes(self):
        """Get all production processes"""
        return self.repository.get_all_processes()
    
    def get_process(self, process_id):
        """Get a production process by its ID"""
        return self.repository.get_process_by_id(process_id)
    
    def get_processes_by_project(self, project_id):
        """Get all production processes for a project"""
        return self.repository.get_processes_by_project(project_id)
    
    def get_processes_by_status(self, status):
        """Get all production processes with a specific status"""
        if status not in ['PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']:
            raise ValueError(f"Invalid status: {status}")
        return self.repository.get_processes_by_status(status)
    
    def get_active_processes(self):
        """Get all production processes that are currently active (planned or in progress)"""
        return self.repository.get_processes_by_status('PLANNED').union(
            self.repository.get_processes_by_status('IN_PROGRESS'))
    
    def get_process_details(self, process_id):
        """Get detailed information about a production process, including inputs and outputs"""
        process = self.repository.get_process_by_id(process_id)
        inputs = self.repository.get_process_inputs(process_id)
        outputs = self.repository.get_process_outputs(process_id)
        
        return {
            'process': process,
            'inputs': inputs,
            'outputs': outputs,
            'efficiency': process.production_efficiency if process.is_complete else None
        }
    
    @transaction.atomic
    def create_process(self, process_data):
        """Create a new production process"""
        # Validate that the target output item exists and is not a raw material
        target_item = self.item_repository.get_item_by_id(process_data['target_output_item_id'])
        if target_item.is_raw_material:
            raise ValueError("Raw materials cannot be produced")
        
        # Additional validation could be done here
        return self.repository.create_process(process_data)
    
    @transaction.atomic
    def start_process(self, process_id, start_date=None):
        """Start a production process"""
        process = self.repository.get_process_by_id(process_id)
        
        if process.status != 'PLANNED':
            raise ValueError(f"Cannot start a process with status: {process.status}")
        
        update_data = {
            'status': 'IN_PROGRESS',
            'process_start_date': start_date
        }
        
        return self.repository.update_process(process_id, update_data)
    
    @transaction.atomic
    def complete_process(self, process_id, end_date=None):
        """Complete a production process"""
        process = self.repository.get_process_by_id(process_id)
        
        if process.status != 'IN_PROGRESS':
            raise ValueError(f"Cannot complete a process with status: {process.status}")
        
        # Check if at least one output has been recorded
        outputs = self.repository.get_process_outputs(process_id)
        if not outputs.exists():
            raise ValueError("Cannot complete a process with no recorded outputs")
        
        update_data = {
            'status': 'COMPLETED',
            'process_end_date': end_date
        }
        
        return self.repository.update_process(process_id, update_data)
    
    @transaction.atomic
    def cancel_process(self, process_id):
        """Cancel a production process"""
        process = self.repository.get_process_by_id(process_id)
        
        if process.status == 'COMPLETED':
            raise ValueError("Cannot cancel a completed process")
        
        update_data = {
            'status': 'CANCELLED',
        }
        
        return self.repository.update_process(process_id, update_data)
    
    @transaction.atomic
    def add_process_input(self, process_id, input_data):
        """Add an input to a production process"""
        # Validate the process
        process = self.repository.get_process_by_id(process_id)
        
        if process.status not in ['PLANNED', 'IN_PROGRESS']:
            raise ValueError(f"Cannot add inputs to a process with status: {process.status}")
        
        # Validate the item
        item = self.item_repository.get_item_by_id(input_data['item_id'])
        
        # Additional validation could be done here
        return self.repository.add_process_input(process_id, input_data)
    
    @transaction.atomic
    def add_process_output(self, process_id, output_data):
        """Add an output to a production process"""
        # Validate the process
        process = self.repository.get_process_by_id(process_id)
        
        if process.status != 'IN_PROGRESS':
            raise ValueError(f"Cannot add outputs to a process with status: {process.status}")
        
        # Validate the item
        item = self.item_repository.get_item_by_id(output_data['item_id'])
        if item.is_raw_material:
            raise ValueError("Raw materials cannot be produced")
        
        # Additional validation could be done here
        return self.repository.add_process_output(process_id, output_data)
    
    @transaction.atomic
    def suggest_inputs_from_bom(self, process_id):
        """Suggest inputs for a production process based on its BOM"""
        process = self.repository.get_process_by_id(process_id)
        
        # Get the BOM for the target output item
        bom_entries = self.bom_repository.get_boms_by_output_item(process.target_output_item_id)
        
        suggested_inputs = []
        for bom_entry in bom_entries:
            suggested_inputs.append({
                'item_id': bom_entry.input_item_id,
                'item_name': bom_entry.input_item.name,
                'quantity_required': bom_entry.quantity_required * process.target_output_quantity,
                'unit_of_measure': bom_entry.unit_of_measure
            })
        
        return suggested_inputs

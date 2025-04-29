from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.inventory.models import ProductionProcess, ProcessItemInput, ProcessItemOutput


class ProductionProcessRepository:
    """
    Repository class for ProductionProcess data access operations.
    Abstracts all database operations related to ProductionProcess model.
    """
    
    def get_all_processes(self):
        """Get all production processes"""
        return ProductionProcess.objects.all()
    
    def get_process_by_id(self, process_id):
        """Get a specific production process by ID"""
        return get_object_or_404(ProductionProcess, id=process_id)
    
    def get_processes_by_project(self, project_id):
        """Get all production processes for a specific project"""
        return ProductionProcess.objects.filter(project_id=project_id)
    
    def get_processes_by_status(self, status):
        """Get all production processes with a specific status"""
        return ProductionProcess.objects.filter(status=status)
    
    def get_processes_by_output_item(self, item_id):
        """Get all production processes for a specific target output item"""
        return ProductionProcess.objects.filter(target_output_item_id=item_id)
    
    def get_processes_by_performer(self, user_id):
        """Get all production processes performed by a specific user"""
        return ProductionProcess.objects.filter(performed_by_id=user_id)
    
    @transaction.atomic
    def create_process(self, process_data):
        """Create a new production process"""
        return ProductionProcess.objects.create(**process_data)
    
    @transaction.atomic
    def update_process(self, process_id, process_data):
        """Update an existing production process"""
        process = self.get_process_by_id(process_id)
        
        for key, value in process_data.items():
            setattr(process, key, value)
        
        process.save()
        return process
    
    @transaction.atomic
    def delete_process(self, process_id):
        """Delete a production process"""
        process = self.get_process_by_id(process_id)
        process.delete()
        return True
    
    def get_process_inputs(self, process_id):
        """Get all inputs for a specific production process"""
        return ProcessItemInput.objects.filter(process_id=process_id)
    
    def get_process_outputs(self, process_id):
        """Get all outputs for a specific production process"""
        return ProcessItemOutput.objects.filter(process_id=process_id)
    
    @transaction.atomic
    def add_process_input(self, process_id, input_data):
        """Add a new input to a production process"""
        input_data['process_id'] = process_id
        return ProcessItemInput.objects.create(**input_data)
    
    @transaction.atomic
    def add_process_output(self, process_id, output_data):
        """Add a new output to a production process"""
        output_data['process_id'] = process_id
        return ProcessItemOutput.objects.create(**output_data)
    
    @transaction.atomic
    def update_process_status(self, process_id, new_status):
        """Update the status of a production process"""
        process = self.get_process_by_id(process_id)
        process.status = new_status
        process.save()
        return process

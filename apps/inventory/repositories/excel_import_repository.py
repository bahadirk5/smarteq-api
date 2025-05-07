from apps.inventory.models.excel_import import ExcelImport


class ExcelImportRepository:
    """
    Repository class for ExcelImport model
    """
    @staticmethod
    def create(import_type, file, notes=None, processed_by=None):
        """
        Create a new Excel import record
        """
        return ExcelImport.objects.create(
            import_type=import_type,
            file=file,
            notes=notes,
            processed_by=processed_by,
            status='PENDING'
        )
    
    @staticmethod
    def get_by_id(import_id):
        """
        Get Excel import by id
        """
        try:
            return ExcelImport.objects.get(id=import_id)
        except ExcelImport.DoesNotExist:
            return None
    
    @staticmethod
    def get_all(order_by='-created_at', **filters):
        """
        Get all Excel imports with optional filters
        """
        return ExcelImport.objects.filter(**filters).order_by(order_by)
    
    @staticmethod
    def get_pending_imports():
        """
        Get all pending Excel imports
        """
        return ExcelImport.objects.filter(status='PENDING').order_by('-created_at')
    
    @staticmethod
    def update_status(import_id, status, processed_count=None, failed_count=None, error_details=None):
        """
        Update Excel import status
        """
        try:
            excel_import = ExcelImport.objects.get(id=import_id)
            excel_import.status = status
            
            if processed_count is not None:
                excel_import.processed_count = processed_count
            
            if failed_count is not None:
                excel_import.failed_count = failed_count
            
            if error_details is not None:
                excel_import.error_details = error_details
            
            excel_import.save()
            return excel_import
        except ExcelImport.DoesNotExist:
            return None
    
    @staticmethod
    def delete(import_id):
        """
        Delete an Excel import record
        """
        try:
            excel_import = ExcelImport.objects.get(id=import_id)
            excel_import.delete()
            return True
        except ExcelImport.DoesNotExist:
            return False

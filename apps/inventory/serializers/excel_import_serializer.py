from rest_framework import serializers
from apps.inventory.models.excel_import import ExcelImport
from apps.users.serializers.user_serializers import UserMinimalSerializer


class ExcelImportSerializer(serializers.ModelSerializer):
    """Serializer for the ExcelImport model"""
    processed_by = UserMinimalSerializer(read_only=True)
    import_type_display = serializers.CharField(source='get_import_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ExcelImport
        fields = [
            'id', 'import_type', 'import_type_display', 'file', 'status', 'status_display',
            'processed_count', 'failed_count', 'error_details', 'notes',
            'processed_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'processed_count', 'failed_count', 'error_details', 
                           'processed_by', 'created_at', 'updated_at', 'status']


class ExcelImportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Excel import records"""
    project_id = serializers.CharField(required=False, write_only=True)
    
    class Meta:
        model = ExcelImport
        fields = ['import_type', 'file', 'notes', 'project_id']


class ExcelTemplateInfoSerializer(serializers.Serializer):
    """Serializer for returning Excel template information"""
    import_type = serializers.CharField()
    template_name = serializers.CharField()
    required_columns = serializers.ListField(child=serializers.CharField())
    optional_columns = serializers.ListField(child=serializers.CharField())
    column_descriptions = serializers.DictField()

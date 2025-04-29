from rest_framework import serializers
from apps.inventory.models import ProductionProcess, ProcessItemInput, ProcessItemOutput, Item
from apps.inventory.serializers.item_serializer import ItemListSerializer
from apps.users.serializers.user_serializers import UserSerializer
from apps.projects.serializers.project_serializer import ProjectSerializer


class ProductionProcessSerializer(serializers.ModelSerializer):
    """Serializer for the ProductionProcess model"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ProductionProcess
        fields = ['id', 'project', 'name', 'description', 'process_start_date', 
                  'process_end_date', 'performed_by', 'status', 'status_display',
                  'target_output_item', 'target_output_quantity', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'status_display']


class ProductionProcessListSerializer(serializers.ModelSerializer):
    """Serializer for listing production processes with minimal information"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    target_item_name = serializers.CharField(source='target_output_item.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ProductionProcess
        fields = ['id', 'name', 'project_name', 'target_item_name', 
                  'status', 'status_display', 'process_start_date', 'process_end_date']


class ProductionProcessDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed production process information including related objects"""
    project_detail = ProjectSerializer(source='project', read_only=True)
    performed_by_detail = UserSerializer(source='performed_by', read_only=True)
    target_output_item_detail = ItemListSerializer(source='target_output_item', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    efficiency = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductionProcess
        fields = ['id', 'project', 'project_detail', 'name', 'description', 
                  'process_start_date', 'process_end_date', 'performed_by', 
                  'performed_by_detail', 'status', 'status_display', 
                  'target_output_item', 'target_output_item_detail', 
                  'target_output_quantity', 'efficiency', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'project_detail', 
                           'performed_by_detail', 'target_output_item_detail', 
                           'status_display', 'efficiency']
    
    def get_efficiency(self, obj):
        if obj.is_complete:
            return obj.production_efficiency
        return None


class ProcessItemInputSerializer(serializers.ModelSerializer):
    """Serializer for the ProcessItemInput model"""
    
    class Meta:
        model = ProcessItemInput
        fields = ['id', 'process', 'item', 'quantity_consumed', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProcessItemInputDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed process input information including item details"""
    item_detail = ItemListSerializer(source='item', read_only=True)
    
    class Meta:
        model = ProcessItemInput
        fields = ['id', 'process', 'item', 'item_detail', 'quantity_consumed', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'item_detail']


class ProcessItemOutputSerializer(serializers.ModelSerializer):
    """Serializer for the ProcessItemOutput model"""
    
    class Meta:
        model = ProcessItemOutput
        fields = ['id', 'process', 'item', 'quantity_produced', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProcessItemOutputDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed process output information including item details"""
    item_detail = ItemListSerializer(source='item', read_only=True)
    
    class Meta:
        model = ProcessItemOutput
        fields = ['id', 'process', 'item', 'item_detail', 'quantity_produced', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'item_detail']


class ProductionProcessSummarySerializer(serializers.ModelSerializer):
    """Serializer for summarizing production process with inputs and outputs"""
    inputs = ProcessItemInputDetailSerializer(many=True, read_only=True)
    outputs = ProcessItemOutputDetailSerializer(many=True, read_only=True)
    target_output_item_detail = ItemListSerializer(source='target_output_item', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    efficiency = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductionProcess
        fields = ['id', 'name', 'status', 'status_display', 'process_start_date', 
                  'process_end_date', 'target_output_item_detail', 
                  'target_output_quantity', 'inputs', 'outputs', 'efficiency']
    
    def get_efficiency(self, obj):
        if obj.is_complete:
            return obj.production_efficiency
        return None

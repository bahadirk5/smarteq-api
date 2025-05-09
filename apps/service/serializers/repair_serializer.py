from rest_framework import serializers
from apps.service.models.repair_request import RepairRequest, RepairStatus
from apps.service.models.repair_part import RepairPart
from apps.sales.serializers.device_serializer import DeviceSerializer
from apps.inventory.serializers.item_serializer import ItemSerializer


class RepairPartSerializer(serializers.ModelSerializer):
    """
    Serializer for RepairPart model.
    """
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        source='item',
        queryset=RepairPart.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    
    class Meta:
        model = RepairPart
        fields = [
            'id', 'repair_request', 'item', 'item_id', 'name', 'quantity',
            'cost', 'total_cost', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'repair_request', 'total_cost', 'created_at', 'updated_at']


class RepairPartListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing RepairPart instances with limited fields.
    """
    item_name = serializers.StringRelatedField(source='item.name', read_only=True)
    repair_number = serializers.StringRelatedField(source='repair_request.repair_number', read_only=True)
    
    class Meta:
        model = RepairPart
        fields = [
            'id', 'repair_request', 'repair_number', 'item_name', 'name', 
            'quantity', 'cost', 'total_cost'
        ]
        read_only_fields = fields


class RepairRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for RepairRequest model.
    """
    device = DeviceSerializer(read_only=True)
    device_id = serializers.PrimaryKeyRelatedField(
        source='device',
        queryset=RepairRequest.objects.all(),
        write_only=True
    )
    parts = RepairPartSerializer(many=True, read_only=True)
    repair_parts = serializers.ListField(
        child=RepairPartSerializer(),
        write_only=True,
        required=False
    )
    
    # Status choices for validation
    status = serializers.ChoiceField(choices=RepairStatus.choices)
    
    # Calculate total parts cost dynamically
    total_parts_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = RepairRequest
        fields = [
            'id', 'repair_number', 'device', 'device_id', 'reported_issue',
            'diagnosis', 'repair_solution', 'status', 'status_notes',
            'is_warranty', 'repair_cost', 'started_at', 'completed_at',
            'technician_notes', 'customer_notes', 'parts', 'repair_parts',
            'total_parts_cost', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'repair_number', 'total_parts_cost', 'created_at', 'updated_at'
        ]
    
    def get_total_parts_cost(self, obj):
        """Calculate total cost of parts used in repair"""
        if not hasattr(obj, 'parts'):
            return 0
        return sum(part.total_cost for part in obj.parts.all())
    
    def create(self, validated_data):
        """
        Create a repair request with nested parts.
        """
        repair_parts_data = validated_data.pop('repair_parts', [])
        repair_request = RepairRequest.objects.create(**validated_data)
        
        for part_data in repair_parts_data:
            RepairPart.objects.create(repair_request=repair_request, **part_data)
        
        return repair_request
    
    def update(self, instance, validated_data):
        """
        Update a repair request with nested parts.
        """
        repair_parts_data = validated_data.pop('repair_parts', None)
        
        # Update RepairRequest instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update repair parts if provided
        if repair_parts_data is not None:
            # Remove existing parts
            instance.parts.all().delete()
            
            # Create new parts
            for part_data in repair_parts_data:
                RepairPart.objects.create(repair_request=instance, **part_data)
        
        return instance


class RepairRequestListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing RepairRequest instances with limited fields.
    """
    device_serial = serializers.StringRelatedField(source='device.serial_number', read_only=True)
    device_item_name = serializers.StringRelatedField(source='device.item.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = RepairRequest
        fields = [
            'id', 'repair_number', 'device_serial', 'device_item_name',
            'status', 'status_display', 'is_warranty', 'repair_cost',
            'started_at', 'completed_at'
        ]
        read_only_fields = fields
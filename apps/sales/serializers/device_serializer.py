from rest_framework import serializers
from apps.sales.models.device import Device
from apps.inventory.serializers.item_serializer import ItemSerializer
from apps.customers.serializers.customer_serializer import CustomerSerializer


class DeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for Device model.
    """
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        source='item',
        queryset=Device.objects.all(),
        write_only=True
    )
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        source='customer',
        queryset=Device.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    
    # Calculate warranty status dynamically
    is_in_warranty = serializers.SerializerMethodField()
    days_left_in_warranty = serializers.SerializerMethodField()
    
    class Meta:
        model = Device
        fields = [
            'id', 'serial_number', 'item', 'item_id', 'customer', 'customer_id',
            'purchase_date', 'warranty_period_months', 'notes', 'status',
            'is_in_warranty', 'days_left_in_warranty', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_in_warranty', 'days_left_in_warranty', 'created_at', 'updated_at']
    
    def get_is_in_warranty(self, obj):
        """Calculate if the device is still in warranty"""
        if hasattr(obj, 'is_in_warranty'):
            return obj.is_in_warranty
        return False
    
    def get_days_left_in_warranty(self, obj):
        """Calculate days left in warranty period"""
        if hasattr(obj, 'days_left_in_warranty'):
            return obj.days_left_in_warranty
        return 0


class DeviceListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Device instances with limited fields.
    """
    item_name = serializers.StringRelatedField(source='item.name', read_only=True)
    item_sku = serializers.StringRelatedField(source='item.sku', read_only=True)
    customer_name = serializers.StringRelatedField(source='customer.name', read_only=True)
    is_in_warranty = serializers.SerializerMethodField()
    
    class Meta:
        model = Device
        fields = [
            'id', 'serial_number', 'item_name', 'item_sku', 'customer_name',
            'purchase_date', 'status', 'is_in_warranty'
        ]
        read_only_fields = ['id', 'item_name', 'item_sku', 'customer_name', 'is_in_warranty']
    
    def get_is_in_warranty(self, obj):
        """Calculate if the device is still in warranty"""
        if hasattr(obj, 'is_in_warranty'):
            return obj.is_in_warranty
        return False
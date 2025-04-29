from rest_framework import serializers
from apps.inventory.models import PurchaseOrderLine, Item
from apps.inventory.serializers.item_serializer import ItemListSerializer


class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    """Serializer for the PurchaseOrderLine model"""
    total_price = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)
    
    class Meta:
        model = PurchaseOrderLine
        fields = ['id', 'purchase_order_id', 'item', 'quantity', 'unit_price', 
                  'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_price']


class PurchaseOrderLineDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed purchase order line information including item details"""
    item_detail = ItemListSerializer(source='item', read_only=True)
    total_price = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)
    
    class Meta:
        model = PurchaseOrderLine
        fields = ['id', 'purchase_order_id', 'item', 'item_detail', 'quantity', 
                  'unit_price', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'item_detail', 'total_price']


class PurchaseOrderLineBulkCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating multiple purchase order lines"""
    
    class Meta:
        model = PurchaseOrderLine
        fields = ['item', 'quantity', 'unit_price']
    
    def validate_item(self, value):
        """Validate that the item exists"""
        if not Item.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid item")
        return value


class PurchaseOrderSummarySerializer(serializers.Serializer):
    """Serializer for summarizing purchase order information"""
    lines = PurchaseOrderLineDetailSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_items = serializers.IntegerField()

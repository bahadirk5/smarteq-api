from rest_framework import serializers
from apps.inventory.models.purchase_history import PurchaseHistory
from apps.inventory.serializers.item_serializer import ItemMinimalSerializer


class PurchaseHistorySerializer(serializers.ModelSerializer):
    """Serializer for the PurchaseHistory model"""
    class Meta:
        model = PurchaseHistory
        fields = [
            'id', 'item', 'purchase_date', 'quantity', 'unit_price', 
            'total_price', 'supplier', 'invoice_reference', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']


class PurchaseHistoryDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for the PurchaseHistory model including item details"""
    item = ItemMinimalSerializer(read_only=True)
    
    class Meta:
        model = PurchaseHistory
        fields = [
            'id', 'item', 'purchase_date', 'quantity', 'unit_price', 
            'total_price', 'supplier', 'invoice_reference', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']


class PurchaseHistoryCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating purchase history records"""
    item_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = PurchaseHistory
        fields = [
            'item_id', 'purchase_date', 'quantity', 'unit_price',
            'supplier', 'invoice_reference', 'notes'
        ]

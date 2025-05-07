from rest_framework import serializers
from apps.inventory.models import InventoryTransaction, Item


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """Serializer for InventoryTransaction model"""
    item_name = serializers.CharField(source='item.name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = ['id', 'item', 'item_name', 'transaction_type', 'transaction_type_display', 
                  'quantity', 'transaction_date', 'reference_model', 'reference_id', 'notes']
        read_only_fields = ['transaction_date']

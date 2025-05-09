from rest_framework import serializers
from apps.sales.models.commission import OrderCommission, CommissionType
from apps.sales.serializers.order_serializer import OrderSerializer


class OrderCommissionSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderCommission model.
    """
    order = OrderSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        source='order',
        queryset=OrderCommission.objects.all(),
        write_only=True
    )
    
    # Commission type choices for validation
    commission_type = serializers.ChoiceField(choices=CommissionType.choices)
    
    class Meta:
        model = OrderCommission
        fields = [
            'id', 'order', 'order_id', 'commission_type', 'amount',
            'percentage', 'third_party_name', 'is_collected',
            'collection_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        

class OrderCommissionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing OrderCommission instances with limited fields.
    """
    order_number = serializers.StringRelatedField(source='order.order_number', read_only=True)
    commission_type_display = serializers.CharField(source='get_commission_type_display', read_only=True)
    
    class Meta:
        model = OrderCommission
        fields = [
            'id', 'order_number', 'commission_type', 'commission_type_display',
            'amount', 'third_party_name', 'is_collected', 'collection_date'
        ]
        read_only_fields = fields
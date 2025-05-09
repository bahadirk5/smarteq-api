from rest_framework import serializers
from apps.sales.models.order import Order, OrderItem, OrderStatus
from apps.dealers.serializers.dealer_serializer import DealerSerializer
from apps.customers.serializers.customer_serializer import CustomerSerializer
from apps.inventory.serializers.item_serializer import ItemSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model.
    """
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        source='item',
        queryset=OrderItem.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'item', 'item_id', 'quantity', 'unit_price',
            'discount_rate', 'tax_rate', 'subtotal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order', 'subtotal', 'created_at', 'updated_at']


class OrderItemListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing OrderItem instances with limited fields.
    """
    item_name = serializers.StringRelatedField(source='item.name', read_only=True)
    order_number = serializers.StringRelatedField(source='order.order_number', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'order_number', 'item_name', 'quantity', 
            'unit_price', 'subtotal'
        ]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model.
    """
    dealer = DealerSerializer(read_only=True)
    dealer_id = serializers.PrimaryKeyRelatedField(
        source='dealer',
        queryset=Order.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        source='customer',
        queryset=Order.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    items = OrderItemSerializer(many=True, read_only=True)
    order_items = serializers.ListField(
        child=OrderItemSerializer(),
        write_only=True,
        required=False
    )
    
    # Status choices for validation
    status = serializers.ChoiceField(choices=OrderStatus.choices)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'dealer', 'dealer_id', 'customer', 'customer_id',
            'order_date', 'status', 'total_amount', 'discount_amount', 
            'tax_amount', 'net_amount', 'is_paid', 'payment_date',
            'shipping_address', 'shipping_cost', 'notes', 'items',
            'order_items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'total_amount', 'discount_amount', 'tax_amount',
            'net_amount', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """
        Create an order with nested order items.
        """
        order_items_data = validated_data.pop('order_items', [])
        order = Order.objects.create(**validated_data)
        
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order
    
    def update(self, instance, validated_data):
        """
        Update an order with nested order items.
        """
        order_items_data = validated_data.pop('order_items', None)
        
        # Update Order instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update order items if provided
        if order_items_data is not None:
            # Remove existing items
            instance.items.all().delete()
            
            # Create new items
            for item_data in order_items_data:
                OrderItem.objects.create(order=instance, **item_data)
        
        return instance


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Order instances with limited fields.
    """
    dealer_name = serializers.StringRelatedField(source='dealer.name', read_only=True)
    customer_name = serializers.StringRelatedField(source='customer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    item_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'dealer_name', 'customer_name',
            'order_date', 'status', 'status_display', 'net_amount', 
            'is_paid', 'item_count'
        ]
        read_only_fields = fields
from rest_framework import serializers
from apps.sales.models.quotation import Quotation, QuotationItem, QuotationStatus
from apps.dealers.serializers.dealer_serializer import DealerSerializer
from apps.customers.serializers.customer_serializer import CustomerSerializer
from apps.inventory.serializers.item_serializer import ItemSerializer


class QuotationItemSerializer(serializers.ModelSerializer):
    """
    Serializer for QuotationItem model.
    """
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        source='item',
        queryset=QuotationItem.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = QuotationItem
        fields = [
            'id', 'quotation', 'item', 'item_id', 'quantity', 'unit_price',
            'discount_rate', 'tax_rate', 'subtotal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'quotation', 'subtotal', 'created_at', 'updated_at']


class QuotationSerializer(serializers.ModelSerializer):
    """
    Serializer for Quotation model.
    """
    dealer = DealerSerializer(read_only=True)
    dealer_id = serializers.PrimaryKeyRelatedField(
        source='dealer',
        queryset=Quotation.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        source='customer',
        queryset=Quotation.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    items = QuotationItemSerializer(many=True, read_only=True)
    quotation_items = serializers.ListField(
        child=QuotationItemSerializer(),
        write_only=True,
        required=False
    )
    
    # Status choices for validation
    status = serializers.ChoiceField(choices=QuotationStatus.choices)
    
    # Calculate validity status dynamically
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Quotation
        fields = [
            'id', 'quotation_number', 'dealer', 'dealer_id', 'customer', 'customer_id',
            'quotation_date', 'valid_until', 'status', 'total_amount', 
            'discount_amount', 'tax_amount', 'net_amount', 'is_valid',
            'pdf_document', 'notes', 'items', 'quotation_items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'quotation_number', 'total_amount', 'discount_amount', 'tax_amount',
            'net_amount', 'is_valid', 'created_at', 'updated_at'
        ]
    
    def get_is_valid(self, obj):
        """Calculate if the quotation is still valid"""
        if hasattr(obj, 'is_valid'):
            return obj.is_valid
        return False
    
    def create(self, validated_data):
        """
        Create a quotation with nested quotation items.
        """
        quotation_items_data = validated_data.pop('quotation_items', [])
        quotation = Quotation.objects.create(**validated_data)
        
        for item_data in quotation_items_data:
            QuotationItem.objects.create(quotation=quotation, **item_data)
        
        return quotation
    
    def update(self, instance, validated_data):
        """
        Update a quotation with nested quotation items.
        """
        quotation_items_data = validated_data.pop('quotation_items', None)
        
        # Update Quotation instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update quotation items if provided
        if quotation_items_data is not None:
            # Remove existing items
            instance.items.all().delete()
            
            # Create new items
            for item_data in quotation_items_data:
                QuotationItem.objects.create(quotation=instance, **item_data)
        
        return instance


class QuotationListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Quotation instances with limited fields.
    """
    dealer_name = serializers.StringRelatedField(source='dealer.name', read_only=True)
    customer_name = serializers.StringRelatedField(source='customer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_valid = serializers.SerializerMethodField()
    item_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = Quotation
        fields = [
            'id', 'quotation_number', 'dealer_name', 'customer_name',
            'quotation_date', 'valid_until', 'status', 'status_display', 
            'net_amount', 'is_valid', 'item_count'
        ]
        read_only_fields = fields
    
    def get_is_valid(self, obj):
        """Calculate if the quotation is still valid"""
        if hasattr(obj, 'is_valid'):
            return obj.is_valid
        return False
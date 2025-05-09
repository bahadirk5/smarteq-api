from rest_framework import serializers
from apps.customers.models.customer import Customer
from apps.dealers.serializers.dealer_serializer import DealerSerializer


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer model.
    """
    dealer = DealerSerializer(read_only=True)
    dealer_id = serializers.PrimaryKeyRelatedField(
        source='dealer', 
        queryset=Customer.objects.filter(is_active=True),
        required=False,
        allow_null=True,
        write_only=True
    )
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'customer_type', 'contact_person', 'email',
            'phone', 'address', 'city', 'state', 'country',
            'postal_code', 'tax_id', 'notes', 'dealer', 'dealer_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Customer instances with limited fields.
    """
    dealer_name = serializers.StringRelatedField(source='dealer.name', read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'customer_type', 'contact_person', 'email',
            'phone', 'city', 'dealer_name'
        ]
        read_only_fields = ['id', 'dealer_name']
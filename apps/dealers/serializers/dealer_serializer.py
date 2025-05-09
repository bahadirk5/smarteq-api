from rest_framework import serializers
from apps.dealers.models.dealer import Dealer


class DealerSerializer(serializers.ModelSerializer):
    """
    Serializer for Dealer model.
    """
    
    class Meta:
        model = Dealer
        fields = [
            'id', 'name', 'code', 'contact_person', 'email',
            'phone', 'address', 'city', 'state', 'country',
            'postal_code', 'discount_rate', 'payment_terms',
            'notes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        

class DealerListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Dealer instances with limited fields.
    """
    
    class Meta:
        model = Dealer
        fields = [
            'id', 'name', 'code', 'contact_person', 'email',
            'phone', 'city', 'is_active'
        ]
        read_only_fields = ['id']
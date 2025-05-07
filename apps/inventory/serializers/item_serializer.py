from rest_framework import serializers
from apps.inventory.models import Item, Category


class ItemSerializer(serializers.ModelSerializer):
    """Serializer for the Item model"""
    
    class Meta:
        model = Item
        fields = ['id', 'name', 'sku', 'description', 'item_type', 'category', 
                  'unit_of_measure', 'quantity', 'selling_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ItemListSerializer(serializers.ModelSerializer):
    """Serializer for listing items with minimal information"""
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Item
        fields = ['id', 'name', 'sku', 'item_type', 'category_name', 'unit_of_measure', 'quantity']


class ItemDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed item information including category details"""
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    
    class Meta:
        model = Item
        fields = ['id', 'name', 'sku', 'description', 'item_type', 'item_type_display', 
                  'category', 'category_name', 'unit_of_measure', 'quantity', 
                  'selling_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_name', 'item_type_display']


class ItemTypeChoiceField(serializers.ChoiceField):
    """Custom choice field for item types with human-readable labels"""
    
    def to_representation(self, value):
        if value in self.choices.keys():
            return {
                'value': value,
                'display': self.choices[value]
            }
        return None


class ItemCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating items with validation"""
    item_type = ItemTypeChoiceField(choices=Item.ITEM_TYPES)
    
    class Meta:
        model = Item
        fields = ['name', 'sku', 'description', 'item_type', 'category', 
                  'unit_of_measure', 'quantity', 'selling_price']
    
    def validate_sku(self, value):
        """Validate that the SKU is unique"""
        instance = getattr(self, 'instance', None)
        if instance and instance.sku == value:
            # If updating an item and the SKU hasn't changed, it's valid
            return value
            
        if Item.objects.filter(sku=value).exists():
            raise serializers.ValidationError("This SKU is already in use")
        return value
    
    def validate_category(self, value):
        """Validate that the category exists"""
        if value and not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid category")
        return value

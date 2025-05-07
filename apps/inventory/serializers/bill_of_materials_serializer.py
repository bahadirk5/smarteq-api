from rest_framework import serializers
from apps.inventory.models import BillOfMaterials, Item
from apps.inventory.serializers.item_serializer import ItemListSerializer


class BillOfMaterialsSerializer(serializers.ModelSerializer):
    """Serializer for the BillOfMaterials model"""
    
    class Meta:
        model = BillOfMaterials
        fields = ['id', 'output_item', 'input_item', 'quantity_required', 
                  'unit_of_measure', 'sequence', 'is_optional', 'is_default',
                  'alternative_group', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BillOfMaterialsDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed BOM information including item details"""
    output_item_detail = ItemListSerializer(source='output_item', read_only=True)
    input_item_detail = ItemListSerializer(source='input_item', read_only=True)
    
    class Meta:
        model = BillOfMaterials
        fields = ['id', 'output_item', 'output_item_detail', 'input_item', 
                  'input_item_detail', 'quantity_required', 'unit_of_measure', 
                  'sequence', 'is_optional', 'is_default', 'alternative_group',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 
                           'output_item_detail', 'input_item_detail']


class BOMComponentSerializer(serializers.ModelSerializer):
    """Serializer for BOM components without output item"""
    input_item_detail = ItemListSerializer(source='input_item', read_only=True)
    
    class Meta:
        model = BillOfMaterials
        fields = ['id', 'input_item', 'input_item_detail', 'quantity_required', 
                  'unit_of_measure', 'sequence', 'is_optional', 'is_default',
                  'alternative_group']
        read_only_fields = ['id', 'input_item_detail']


class BOMComponentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating BOM components"""
    
    class Meta:
        model = BillOfMaterials
        fields = ['input_item', 'quantity_required', 'unit_of_measure', 'sequence',
                 'is_optional', 'is_default', 'alternative_group']
    
    def validate_input_item(self, value):
        """Validate that the input item exists"""
        if not Item.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid input item")
        return value


class BOMHierarchySerializer(serializers.Serializer):
    """Serializer for representing a recursive bill of materials"""
    item_id = serializers.UUIDField()
    item_name = serializers.CharField()
    item_sku = serializers.CharField()
    item_type = serializers.CharField()
    components = serializers.ListField(child=serializers.DictField())


class CustomizableBOMSerializer(serializers.Serializer):
    """Serializer for representing a customizable bill of materials with alternatives"""
    component = BOMComponentSerializer()
    alternatives = BOMComponentSerializer(many=True)


class ProductCustomizationSerializer(serializers.Serializer):
    """Serializer for customizing a product with specific component selections"""
    group = serializers.CharField()
    component_id = serializers.IntegerField()


class MaterialRequirementSerializer(serializers.Serializer):
    """Serializer for material requirements calculation results"""
    item = ItemListSerializer()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=3)
    unit_of_measure = serializers.CharField()
    available_quantity = serializers.IntegerField()
    is_sufficient = serializers.BooleanField()

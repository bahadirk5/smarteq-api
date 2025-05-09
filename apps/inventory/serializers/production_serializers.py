from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.inventory.models.production import Production
from apps.inventory.models.production_item import ProductionItem
from apps.inventory.models.production_history import ProductionHistory
from apps.inventory.serializers.recipe_serializers import RecipeSerializer
from apps.inventory.serializers.item_serializer import ItemSerializer


class ProductionItemSerializer(serializers.ModelSerializer):
    """Serializer for the ProductionItem model"""
    item_details = ItemSerializer(source='input_item', read_only=True)
    
    class Meta:
        model = ProductionItem
        fields = [
            'id', 'production', 'input_item', 'item_details', 
            'quantity_consumed', 'unit_of_measure',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductionItemCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating ProductionItems"""
    
    class Meta:
        model = ProductionItem
        fields = [
            'production', 'input_item', 'quantity_consumed', 'unit_of_measure'
        ]


class ProductionHistorySerializer(serializers.ModelSerializer):
    """Serializer for the ProductionHistory model"""
    performed_by_username = serializers.CharField(source='performed_by.username', read_only=True)
    
    class Meta:
        model = ProductionHistory
        fields = [
            'id', 'production', 'action', 'performed_by', 'performed_by_username',
            'timestamp', 'notes', 'previous_data', 'new_data'
        ]
        read_only_fields = ['id', 'timestamp']


class ProductionSerializer(serializers.ModelSerializer):
    """Serializer for the Production model"""
    recipe_details = RecipeSerializer(source='recipe', read_only=True)
    executed_by_username = serializers.CharField(source='executed_by.username', read_only=True)
    consumed_items = ProductionItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Production
        fields = [
            'id', 'recipe', 'recipe_details', 'output_quantity',
            'executed_by', 'executed_by_username', 'execution_date', 'notes',
            'consumed_items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'execution_date', 'created_at', 'updated_at']


class ProductionDetailSerializer(ProductionSerializer):
    """Detailed serializer for the Production model"""
    history = ProductionHistorySerializer(many=True, read_only=True)
    
    class Meta(ProductionSerializer.Meta):
        fields = ProductionSerializer.Meta.fields + ['history']


class ProductionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Production records"""
    consumed_items = ProductionItemCreateUpdateSerializer(many=True, required=False)
    
    class Meta:
        model = Production
        fields = ['recipe', 'output_quantity', 'notes', 'consumed_items']
        
    def create(self, validated_data):
        consumed_items_data = validated_data.pop('consumed_items', [])
        
        # Create the production record
        production = Production.objects.create(**validated_data)
        
        # Create the production items
        for item_data in consumed_items_data:
            ProductionItem.objects.create(production=production, **item_data)
            
        # Create history record
        ProductionHistory.objects.create(
            production=production,
            action='Created',
            performed_by=validated_data['executed_by'],
            notes=f"Production created with {len(consumed_items_data)} consumed items",
            new_data=validated_data
        )
        
        return production


class ProductionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Production records"""
    consumed_items = ProductionItemCreateUpdateSerializer(many=True, required=False)
    
    class Meta:
        model = Production
        fields = ['output_quantity', 'notes', 'consumed_items']
        
    def update(self, instance, validated_data):
        consumed_items_data = validated_data.pop('consumed_items', None)
        
        # Store original data for history
        previous_data = {
            'output_quantity': str(instance.output_quantity),
            'notes': instance.notes
        }
        
        # Update the production record
        instance.output_quantity = validated_data.get('output_quantity', instance.output_quantity)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()
        
        # Update production items if provided
        if consumed_items_data is not None:
            # First, remove existing items
            instance.consumed_items.all().delete()
            
            # Then create new ones
            for item_data in consumed_items_data:
                ProductionItem.objects.create(production=instance, **item_data)
        
        # Create history record
        ProductionHistory.objects.create(
            production=instance,
            action='Updated',
            performed_by=self.context['request'].user,
            notes="Production updated",
            previous_data=previous_data,
            new_data=validated_data
        )
        
        return instance

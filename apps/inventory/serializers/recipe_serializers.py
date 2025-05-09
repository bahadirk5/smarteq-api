from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.inventory.models.recipe import Recipe
from apps.inventory.models.recipe_item import RecipeItem
from apps.inventory.serializers.item_serializer import ItemSerializer


class RecipeItemSerializer(serializers.ModelSerializer):
    """Serializer for the RecipeItem model"""
    item_details = ItemSerializer(source='input_item', read_only=True)
    
    class Meta:
        model = RecipeItem
        fields = [
            'id', 'recipe', 'input_item', 'item_details', 'quantity_required',
            'unit_of_measure', 'sequence', 'is_optional', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecipeItemCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating RecipeItems"""
    
    class Meta:
        model = RecipeItem
        fields = [
            'recipe', 'input_item', 'quantity_required',
            'unit_of_measure', 'sequence', 'is_optional', 'notes'
        ]
        
    def validate(self, data):
        """Validate that input_item and recipe are compatible"""
        recipe = data.get('recipe')
        input_item = data.get('input_item')
        
        # Avoid circular dependencies (a recipe using itself as an ingredient)
        if recipe and input_item and recipe.output_item.id == input_item.id:
            raise serializers.ValidationError(_('A recipe cannot use its own output item as an ingredient'))
            
        return data


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the Recipe model"""
    output_item_details = ItemSerializer(source='output_item', read_only=True)
    items = RecipeItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'output_item', 'output_item_details',
            'output_quantity', 'unit_of_measure', 'active', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'items', 'created_at', 'updated_at']


class RecipeDetailSerializer(RecipeSerializer):
    """Detailed serializer for the Recipe model"""
    
    class Meta(RecipeSerializer.Meta):
        pass


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Recipes"""
    
    class Meta:
        model = Recipe
        fields = [
            'name', 'description', 'output_item',
            'output_quantity', 'unit_of_measure', 'active'
        ]

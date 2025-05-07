from rest_framework import serializers
from apps.inventory.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model"""
    parent_category_id = serializers.UUIDField(source='parent_category.id', required=False, allow_null=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent_category', 'parent_category_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'parent_category': {'write_only': True, 'required': False}
        }


class CategoryListSerializer(serializers.ModelSerializer):
    """Serializer for listing categories with minimal information"""
    
    class Meta:
        model = Category
        fields = ['id', 'name']


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed category information including parent details"""
    parent_name = serializers.CharField(source='parent_category.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent_category', 'parent_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'parent_name']


class CategoryHierarchySerializer(serializers.ModelSerializer):
    """Serializer for nested category hierarchies"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'children']
    
    def get_children(self, obj):
        children = Category.objects.filter(parent_category=obj)
        serializer = CategoryHierarchySerializer(children, many=True)
        return serializer.data

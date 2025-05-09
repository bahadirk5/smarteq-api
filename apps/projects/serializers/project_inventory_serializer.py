from rest_framework import serializers
from apps.projects.models import ProjectInventory
from apps.inventory.serializers.item_serializer import ItemSerializer


class ProjectInventorySerializer(serializers.ModelSerializer):
    """
    Serializer for the ProjectInventory model.
    """
    class Meta:
        model = ProjectInventory
        fields = ['id', 'project', 'item', 'quantity', 'minimum_stock_level', 'notes', 'created_at', 'updated_at']


class ProjectInventoryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the ProjectInventory model with nested item details.
    """
    item_details = ItemSerializer(source='item', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectInventory
        fields = ['id', 'project', 'project_name', 'item', 'item_details', 'quantity', 
                  'minimum_stock_level', 'stock_status', 'notes', 'created_at', 'updated_at']
    
    def get_stock_status(self, obj):
        """
        Calculate stock status based on current quantity vs minimum level.
        
        Returns:
            str: 'low', 'ok', or 'excess'
        """
        if obj.quantity < obj.minimum_stock_level:
            return 'low'
        elif obj.quantity == obj.minimum_stock_level:
            return 'ok'
        else:
            return 'excess'

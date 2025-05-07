from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.common.responses import success_response, error_response
from apps.inventory.services.customizable_product_service import CustomizableProductService
from apps.inventory.serializers.bill_of_materials_serializer import (
    CustomizableBOMSerializer,
    ProductCustomizationSerializer,
    MaterialRequirementSerializer
)
from apps.inventory.serializers.item_serializer import ItemDetailSerializer


class ProductBOMView(APIView):
    """
    API endpoint for viewing a product's bill of materials structure
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, item_id):
        """
        Get the bill of materials for a product, organized by customizable component groups
        """
        bom_structure, error = CustomizableProductService.get_product_bom(item_id)
        
        if error:
            return error_response(error, status.HTTP_400_BAD_REQUEST)
        
        serializer = CustomizableBOMSerializer(bom_structure, many=True)
        return success_response(serializer.data)


class ProductCustomizationView(APIView):
    """
    API endpoint for customizing a product and calculating material requirements
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, item_id):
        """
        Create a customized variant of a product with selected components
        
        Expected request body format:
        {
            "component_selections": [
                {
                    "group": "group_name",
                    "component_id": component_id
                },
                ...
            ]
        }
        """
        component_selections = request.data.get('component_selections', [])
        
        # Validate component selections
        serializer = ProductCustomizationSerializer(data=component_selections, many=True)
        if not serializer.is_valid():
            return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        customized_bom, error = CustomizableProductService.customize_product(
            item_id=item_id,
            component_selections=serializer.validated_data
        )
        
        if error:
            return error_response(error, status.HTTP_400_BAD_REQUEST)
        
        # Return the customized BOM structure
        return success_response({
            'message': 'Product customized successfully',
            'customized_bom': CustomizableBOMSerializer(customized_bom, many=True).data
        })


class MaterialRequirementsView(APIView):
    """
    API endpoint for calculating material requirements for a product
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, item_id):
        """
        Calculate material requirements for producing a product
        
        Expected request body format:
        {
            "quantity": 1,  # Optional, default: 1
            "component_selections": [  # Optional
                {
                    "group": "group_name",
                    "component_id": component_id
                },
                ...
            ]
        }
        """
        quantity = int(request.data.get('quantity', 1))
        component_selections = request.data.get('component_selections', [])
        
        # Validate component selections if provided
        if component_selections:
            selections_serializer = ProductCustomizationSerializer(data=component_selections, many=True)
            if not selections_serializer.is_valid():
                return error_response(selections_serializer.errors, status.HTTP_400_BAD_REQUEST)
            component_selections = selections_serializer.validated_data
        
        # Calculate material requirements
        requirements, error = CustomizableProductService.calculate_material_requirements(
            item_id=item_id,
            quantity=quantity,
            component_selections=component_selections
        )
        
        if error:
            return error_response(error, status.HTTP_400_BAD_REQUEST)
        
        # Transform the requirements dict to a list for serialization
        requirements_list = []
        for item_id, req in requirements.items():
            # Add a flag indicating if there's enough inventory
            req['is_sufficient'] = req['available_quantity'] >= req['quantity']
            requirements_list.append(req)
        
        # Sort by is_sufficient flag (insufficient first) and then by item name
        requirements_list.sort(key=lambda x: (x['is_sufficient'], x['item'].name))
        
        return success_response({
            'material_requirements': requirements_list
        })


class ProductionView(APIView):
    """
    API endpoint for producing products
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, item_id):
        """
        Produce a product by consuming required raw materials
        
        Expected request body format:
        {
            "quantity": 1,  # Optional, default: 1
            "component_selections": [  # Optional
                {
                    "group": "group_name",
                    "component_id": component_id
                },
                ...
            ]
        }
        """
        quantity = int(request.data.get('quantity', 1))
        component_selections = request.data.get('component_selections', [])
        
        # Validate component selections if provided
        if component_selections:
            selections_serializer = ProductCustomizationSerializer(data=component_selections, many=True)
            if not selections_serializer.is_valid():
                return error_response(selections_serializer.errors, status.HTTP_400_BAD_REQUEST)
            component_selections = selections_serializer.validated_data
        
        # Produce the product
        result, error = CustomizableProductService.produce_product(
            item_id=item_id,
            quantity=quantity,
            component_selections=component_selections
        )
        
        if error:
            return error_response(error, status.HTTP_400_BAD_REQUEST)
        
        # Return production details
        return success_response({
            'message': f'Successfully produced {quantity} units',
            'product': ItemDetailSerializer(result['product']).data,
            'quantity_produced': result['quantity_produced']
        })


class SalesListView(APIView):
    """
    API endpoint for managing product sales lists
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, item_id):
        """
        Update the sales list status for a product
        
        Expected request body format:
        {
            "sales_list_status": "NOT_LISTED" | "CUSTOMER_LIST" | "DEALER_LIST" | "BOTH_LISTS"
        }
        """
        from apps.inventory.repositories.item_repository import ItemRepository
        
        status_value = request.data.get('sales_list_status')
        if not status_value or status_value not in ['NOT_LISTED', 'CUSTOMER_LIST', 'DEALER_LIST', 'BOTH_LISTS']:
            return error_response('Invalid sales list status', status.HTTP_400_BAD_REQUEST)
        
        item = ItemRepository.get_by_id(item_id)
        if not item:
            return error_response('Item not found', status.HTTP_404_NOT_FOUND)
        
        updated_item = ItemRepository.update(item_id, sales_list_status=status_value)
        
        return success_response({
            'message': 'Sales list status updated successfully',
            'item': ItemDetailSerializer(updated_item).data
        })

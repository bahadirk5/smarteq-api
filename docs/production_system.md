# SmartEQ Manufacturing and Production System

## Overview

The new manufacturing and production system replaces the legacy `BillOfMaterials` approach with a more robust, flexible recipe-based system that supports:

1. Multiple raw materials and intermediate products in a single recipe
2. Complete production history and audit trails
3. Automatic inventory adjustments
4. Recipe versioning and modifications

## API Endpoints

### Recipe Management

Endpoints are available under the `/api/v1/inventory/` path.

#### List all recipes

```
GET /api/v1/inventory/recipes/
```

#### Get recipe details

```
GET /api/v1/inventory/recipes/{recipe_id}/
```

#### Create a new recipe

```
POST /api/v1/inventory/recipes/
```

Required fields:
- name: string
- description: string
- output_item: UUID (item_id)
- output_quantity: decimal
- unit_of_measure: string

#### Update a recipe

```
PUT /api/v1/inventory/recipes/{recipe_id}/
PATCH /api/v1/inventory/recipes/{recipe_id}/
```

#### Delete a recipe

```
DELETE /api/v1/inventory/recipes/{recipe_id}/
```

#### Recipe Item Management

```
GET /api/v1/inventory/recipe-items/
GET /api/v1/inventory/recipe-items/{recipe_item_id}/
POST /api/v1/inventory/recipe-items/
PUT /api/v1/inventory/recipe-items/{recipe_item_id}/
PATCH /api/v1/inventory/recipe-items/{recipe_item_id}/
DELETE /api/v1/inventory/recipe-items/{recipe_item_id}/
```

### Production Management

#### List all productions

```
GET /api/v1/inventory/productions/
```

#### Get production details

```
GET /api/v1/inventory/productions/{production_id}/
```

#### Create a new production record

```
POST /api/v1/inventory/productions/
```

Required fields:
- recipe: UUID (recipe_id)
- output_quantity: decimal
- executed_by: UUID (user_id)
- notes: string (optional)

#### Update a production record

```
PUT /api/v1/inventory/productions/{production_id}/
PATCH /api/v1/inventory/productions/{production_id}/
```

#### Delete a production record

```
DELETE /api/v1/inventory/productions/{production_id}/
```
```
GET /api/v1/recipes/
```
Query parameters:
- `name`: Filter by recipe name (partial match)
- `output_item_id`: Filter by output item ID
- `active`: Filter by active status (true/false)

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Example Recipe",
      "description": "Recipe description",
      "output_item": "uuid",
      "output_item_details": { /* Item details */ },
      "output_quantity": 1.0,
      "unit_of_measure": "units",
      "active": true,
      "items": [
        {
          "id": "uuid",
          "recipe": "uuid",
          "input_item": "uuid",
          "item_details": { /* Item details */ },
          "quantity_required": 2.0,
          "unit_of_measure": "kg",
          "sequence": 10,
          "is_optional": false,
          "notes": "Additional notes",
          "created_at": "timestamp",
          "updated_at": "timestamp"
        }
      ],
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ]
}
```

#### Get a specific recipe
```
GET /api/v1/recipes/{recipe_id}/
```
Response: Same as above but for a single recipe with more detailed information.

#### Create a new recipe
```
POST /api/v1/recipes/
```
Request body:
```json
{
  "name": "New Recipe",
  "description": "Recipe description",
  "output_item": "uuid",
  "output_quantity": 1.0,
  "unit_of_measure": "units",
  "active": true,
  "items": [
    {
      "input_item": "uuid",
      "quantity_required": 2.0,
      "unit_of_measure": "kg",
      "sequence": 10,
      "is_optional": false,
      "notes": "Component notes"
    }
  ]
}
```

#### Update a recipe
```
PUT /api/v1/recipes/{recipe_id}/
```
Request body: Same as create, but fields are optional for partial updates.

#### Delete a recipe
```
DELETE /api/v1/recipes/{recipe_id}/
```

#### Get recipe items
```
GET /api/v1/recipes/{recipe_id}/items/
```

#### Add an item to a recipe
```
POST /api/v1/recipes/{recipe_id}/items/
```
Request body:
```json
{
  "input_item": "uuid",
  "quantity_required": 2.0,
  "unit_of_measure": "kg",
  "sequence": 10,
  "is_optional": false,
  "notes": "Component notes"
}
```

### Recipe Item Management

#### Update a recipe item
```
PUT /api/v1/recipe-items/{recipe_item_id}/
```

#### Delete a recipe item
```
DELETE /api/v1/recipe-items/{recipe_item_id}/
```

### Production Management

#### List all productions
```
GET /api/v1/productions/
```
Query parameters:
- `recipe_id`: Filter by recipe ID
- `executed_by_id`: Filter by user ID who executed the production
- `date_from`: Filter by date range (start date)
- `date_to`: Filter by date range (end date)

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "recipe": "uuid",
      "recipe_details": { /* Recipe details */ },
      "output_quantity": 10.0,
      "executed_by": "uuid",
      "executed_by_username": "username",
      "execution_date": "timestamp",
      "notes": "Production notes",
      "consumed_items": [
        {
          "id": "uuid",
          "production": "uuid",
          "input_item": "uuid",
          "item_details": { /* Item details */ },
          "quantity_consumed": 2.0,
          "unit_of_measure": "kg",
          "created_at": "timestamp",
          "updated_at": "timestamp"
        }
      ],
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ]
}
```

#### Get a specific production
```
GET /api/v1/productions/{production_id}/
```
Response: Same as above but for a single production with more detailed information including history.

#### Create a new production
```
POST /api/v1/productions/
```
Request body:
```json
{
  "recipe": "uuid",
  "output_quantity": 10.0,
  "notes": "Production notes",
  "consumed_items": [
    {
      "input_item": "uuid",
      "quantity_consumed": 2.0,
      "unit_of_measure": "kg"
    }
  ]
}
```
Notes:
- If `consumed_items` is not provided, the system will automatically calculate the required quantities based on the recipe and output quantity.
- Inventory is automatically adjusted when a production is created.

#### Update a production
```
PUT /api/v1/productions/{production_id}/
```
Request body:
```json
{
  "output_quantity": 12.0,
  "notes": "Updated production notes",
  "consumed_items": [
    {
      "input_item": "uuid",
      "quantity_consumed": 2.5,
      "unit_of_measure": "kg"
    }
  ]
}
```
Notes:
- Inventory will be automatically adjusted based on the changes.
- All changes are tracked in the production history.

#### Get production history
```
GET /api/v1/productions/{production_id}/history/
```
Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "production": "uuid",
      "action": "Created",
      "performed_by": "uuid",
      "performed_by_username": "username",
      "timestamp": "timestamp",
      "notes": "Production created",
      "previous_data": null,
      "new_data": { /* New data details */ }
    }
  ]
}
```

#### Get productions by recipe
```
GET /api/v1/productions/by_recipe/{recipe_id}/
```
Response: List of productions filtered by the specified recipe.

## Frontend Implementation Guidelines

### Recipe Management UI

1. **Recipe List View**
   - Display a table of recipes with columns for name, output item, quantity, and status
   - Include filter options for name, output item, and active status
   - Provide "Create New" button and edit/delete actions for each recipe

2. **Recipe Detail View**
   - Display recipe details including name, description, output item and quantity
   - Show a table of all input items with their quantities and properties
   - Include options to add, edit, or remove input items
   - Provide a "Produce" button to create a new production from this recipe

3. **Recipe Form**
   - Form fields for recipe name, description, output item (select), quantity, and unit of measure
   - Dynamic form section for adding multiple input items
   - For each input item: input item selector, quantity, unit of measure, sequence number, and optional flag

### Production Management UI

1. **Production List View**
   - Display a table of productions with columns for date, recipe, output quantity, and executed by
   - Include filter options for recipe, date range, and user
   - Provide view details action for each production

2. **Production Detail View**
   - Display production details including recipe, output quantity, execution date, and user
   - Show a table of all consumed items with their quantities
   - Include a history tab showing all changes made to this production

3. **Production Form**
   - Select recipe (which auto-populates related fields)
   - Set output quantity (which auto-calculates required input quantities)
   - Option to customize input quantities if needed
   - Notes field for additional information

## Error Handling

The API returns standardized error responses:

```json
{
  "success": false,
  "message": "Error message",
  "status_code": 400
}
```

Common error scenarios to handle in the frontend:

1. Insufficient inventory for production
2. Circular dependencies in recipes (using an item in its own recipe)
3. Missing required fields
4. Server errors

## Migration from BillOfMaterials

The legacy `BillOfMaterials` API endpoint will continue to function until all clients have migrated to the new system, but it is marked as deprecated and will be removed in a future version.

To migrate from BillOfMaterials to the new Recipe system:

1. Create new Recipes for each unique output item in BillOfMaterials
2. Add RecipeItems for each input item associated with that output item
3. Update frontend code to use the new endpoints

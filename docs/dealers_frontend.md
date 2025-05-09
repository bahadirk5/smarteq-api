# Dealers Module - Frontend Implementation Guide

## Overview

The Dealers module handles dealer management across the SmartEQ platform. It provides functionality for managing dealers who are business partners that sell and distribute products to customers, including tracking their contact information and relationships with customers.

## API Endpoints

### Dealer Management

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/v1/dealers/dealers/` | GET | List all dealers | None | List of dealers |
| `/api/v1/dealers/dealers/` | POST | Create a new dealer | Dealer object | Created dealer |
| `/api/v1/dealers/dealers/{id}/` | GET | Get dealer details | None | Dealer details |
| `/api/v1/dealers/dealers/{id}/` | PUT | Update a dealer | Dealer object | Updated dealer |
| `/api/v1/dealers/dealers/{id}/` | DELETE | Delete a dealer | None | Success message |
| `/api/v1/dealers/dealers/active/` | GET | Get only active dealers | None | List of active dealers |
| `/api/v1/dealers/dealers/{id}/activate/` | PUT | Activate a dealer | None | Updated dealer |
| `/api/v1/dealers/dealers/{id}/deactivate/` | PUT | Deactivate a dealer | None | Updated dealer |
| `/api/v1/dealers/dealers/{id}/customers/` | GET | List customers of a dealer | None | List of customers |

## Frontend Implementation Guidelines

### Dealer Management Interface

1. **Dealer List View**
   - Display paginated list of dealers with search/filter options
   - Show key attributes like name, code, contact information
   - Include filter for active/inactive dealers
   - Include actions for view, edit, delete based on user permissions

2. **Dealer Detail View**
   - Show comprehensive dealer information
   - Include sections for contact details, address, and tax information
   - Display list of customers associated with the dealer
   - Provide quick actions to view customer details
   - Show activation status and provide activate/deactivate controls

3. **Dealer Create/Edit Form**
   - Form with fields for all dealer attributes
   - Validation for required fields and formats (e.g., email, phone)
   - Input masking for formatted fields like phone and tax ID
   - Client-side validation before submission

### Dealer-Customer Relationship Management

1. **Customer Assignment Interface**
   - View all customers assigned to a dealer
   - Filter and search capabilities for customer list
   - Easy navigation between dealer and customer records

## Data Models

### Dealer Model

```typescript
interface Dealer {
  id: string;
  name: string;
  code: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  tax_id?: string;
  tax_office?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

### Dealer List Item Model

```typescript
interface DealerListItem {
  id: string;
  name: string;
  code: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  is_active: boolean;
}
```

## Error Handling

- Implement appropriate error handling for all API requests
- Display meaningful error messages to users
- Handle validation errors for required and unique fields
- Show loading states during API calls

## Security Considerations

1. **Authorization**
   - Implement role-based access control in UI
   - Hide UI elements based on user permissions
   - Ensure proper access control for dealer management functions

2. **Form Security**
   - Implement proper input validation
   - Sanitize inputs to prevent XSS attacks
   - Validate uniqueness of dealer codes

## UI/UX Recommendations

1. **Dealer Management**
   - Sortable and filterable dealer lists
   - Quick search by dealer name, code, or contact information
   - Clear indication of dealer activation status
   - Confirmation dialogs for critical actions (delete, deactivate)

2. **Dealer Creation Workflow**
   - Step-by-step form for creating new dealers
   - Code generation assistance or validation
   - Form validation with clear error messages
   - Preview before submission

3. **Dashboard Integration**
   - Show dealer statistics in dashboard
   - Recent dealer activities
   - Dealer performance metrics
   - Map visualization of dealer locations (if geographical data is available)
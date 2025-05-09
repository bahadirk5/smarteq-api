# Customers Module - Frontend Implementation Guide

## Overview

The Customers module handles customer management across the SmartEQ platform. It provides functionality for managing both individual and corporate customers, including their relationships with dealers, devices, and orders.

## API Endpoints

### Customer Management

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/v1/customers/customers/` | GET | List all customers | None | List of customers |
| `/api/v1/customers/customers/` | POST | Create a new customer | Customer object | Created customer |
| `/api/v1/customers/customers/{id}/` | GET | Get customer details | None | Customer details |
| `/api/v1/customers/customers/{id}/` | PUT | Update a customer | Customer object | Updated customer |
| `/api/v1/customers/customers/{id}/` | DELETE | Delete a customer | None | Success message |
| `/api/v1/customers/customers/by_dealer/` | GET | Filter customers by dealer | `?dealer_id=<id>` | List of customers |
| `/api/v1/customers/customers/by_type/` | GET | Filter customers by type | `?type=<individual/corporate>` | List of customers |
| `/api/v1/customers/customers/{id}/devices/` | GET | Get customer's devices | None | List of devices |
| `/api/v1/customers/customers/{id}/orders/` | GET | Get customer's orders | None | List of orders |

## Frontend Implementation Guidelines

### Customer Management Interface

1. **Customer List View**
   - Display paginated list of customers with search/filter options
   - Show key attributes like name, type (individual/corporate), contact information
   - Include filter by dealer and customer type
   - Include actions for view, edit, delete based on user permissions

2. **Customer Detail View**
   - Show comprehensive customer information
   - Include sections for personal/corporate details
   - Display linked devices and orders
   - Provide quick actions to view device details or order history

3. **Customer Create/Edit Form**
   - Form with fields for all customer attributes
   - Different fields for individual vs corporate customers
   - Dealer selection via dropdown
   - Validation for required fields and formats

### Customer-Dealer Relationship Management

1. **Dealer Assignment Interface**
   - Allow assigning customers to dealers
   - Show relationship between customers and dealers
   - Enable bulk assignment of customers to dealers if needed

### Customer Device Management

1. **Device Association Interface**
   - View and manage devices associated with customers
   - Link from customer detail view to device details
   - Show device status and history

### Customer Order Management

1. **Order Management Interface**
   - View orders placed by customers
   - Link from customer detail view to order details
   - Show order status and history

## Data Models

### Customer Model

```typescript
interface Customer {
  id: string;
  name: string;
  customer_type: "individual" | "corporate";
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  tax_id?: string;
  tax_office?: string;
  dealer_id: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}
```

### Customer List Item Model

```typescript
interface CustomerListItem {
  id: string;
  name: string;
  customer_type: "individual" | "corporate";
  email?: string;
  phone?: string;
  dealer_id: string;
  dealer_name: string;
}
```

## Error Handling

- Implement appropriate error handling for all API requests
- Display meaningful error messages to users
- Handle validation errors from the API with clear feedback
- Show loading states during API calls

## Security Considerations

1. **Authorization**
   - Implement role-based access control in UI
   - Hide UI elements based on user permissions
   - Ensure proper access control for sensitive customer data

2. **Form Security**
   - Implement proper input validation
   - Sanitize inputs to prevent XSS attacks
   - Protect personal/sensitive information

## UI/UX Recommendations

1. **Customer Management**
   - Sortable and filterable customer lists
   - Quick search by customer name, email, or phone
   - Customer type indicators (individual/corporate)
   - Clear indication of the associated dealer

2. **Customer Creation Workflow**
   - Step-by-step form for creating new customers
   - Auto-suggest fields where appropriate
   - Form validation with clear error messages
   - Preview before submission

3. **Dashboard Integration**
   - Show customer statistics in dashboard
   - Recent customer activities
   - Customer growth trends
   - Top customers by order volume
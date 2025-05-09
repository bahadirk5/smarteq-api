# Sales Module - Frontend Implementation Guide

## Overview

The Sales module handles all sales-related operations across the SmartEQ platform. It provides functionality for managing orders, quotations, devices, and commissions, tracking the entire sales process from initial quotation to order fulfillment and device delivery.

## API Endpoints

### Order Management

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/v1/sales/orders/` | GET | List all orders | None | List of orders |
| `/api/v1/sales/orders/` | POST | Create a new order | Order object | Created order |
| `/api/v1/sales/orders/{id}/` | GET | Get order details | None | Order details |
| `/api/v1/sales/orders/{id}/` | PUT | Update an order | Order object | Updated order |
| `/api/v1/sales/orders/{id}/` | DELETE | Delete an order | None | Success message |
| `/api/v1/sales/orders/by_dealer/{dealer_id}/` | GET | Get orders for a specific dealer | None | List of orders |
| `/api/v1/sales/orders/{id}/items/` | GET | Get order items | None | List of order items |
| `/api/v1/sales/orders/{id}/update_status/` | PUT | Update order status | `{ "status": "confirmed" }` | Updated order |
| `/api/v1/sales/orders/{id}/mark_paid/` | PUT | Mark order as paid | None | Updated order |

### Quotation Management

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/v1/sales/quotations/` | GET | List all quotations | None | List of quotations |
| `/api/v1/sales/quotations/` | POST | Create a new quotation | Quotation object | Created quotation |
| `/api/v1/sales/quotations/{id}/` | GET | Get quotation details | None | Quotation details |
| `/api/v1/sales/quotations/{id}/` | PUT | Update a quotation | Quotation object | Updated quotation |
| `/api/v1/sales/quotations/{id}/` | DELETE | Delete a quotation | None | Success message |
| `/api/v1/sales/quotations/{id}/convert_to_order/` | POST | Convert quotation to order | None | Created order |

### Device Management

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/v1/sales/devices/` | GET | List all devices | None | List of devices |
| `/api/v1/sales/devices/` | POST | Register a new device | Device object | Created device |
| `/api/v1/sales/devices/{id}/` | GET | Get device details | None | Device details |
| `/api/v1/sales/devices/{id}/` | PUT | Update a device | Device object | Updated device |
| `/api/v1/sales/devices/{id}/` | DELETE | Delete a device | None | Success message |
| `/api/v1/sales/devices/by_customer/{customer_id}/` | GET | Get devices for a specific customer | None | List of devices |
| `/api/v1/sales/devices/by_serial/{serial_number}/` | GET | Get device by serial number | None | Device details |
| `/api/v1/sales/devices/{id}/warranty_status/` | GET | Check device warranty status | None | Warranty status |

### Commission Management

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/v1/sales/commissions/` | GET | List all commissions | None | List of commissions |
| `/api/v1/sales/commissions/` | POST | Create a commission record | Commission object | Created commission |
| `/api/v1/sales/commissions/{id}/` | GET | Get commission details | None | Commission details |
| `/api/v1/sales/commissions/{id}/` | PUT | Update a commission | Commission object | Updated commission |
| `/api/v1/sales/commissions/by_dealer/{dealer_id}/` | GET | Get commissions for a dealer | None | List of commissions |

## Frontend Implementation Guidelines

### Order Management Interface

1. **Order List View**
   - Display paginated list of orders with search/filter options
   - Show key attributes like order number, dealer, date, status, and total price
   - Include filters for status, date range, and dealer
   - Include actions for view, edit, delete based on user permissions
   - Color-coded status indicators

2. **Order Detail View**
   - Show comprehensive order information
   - Display order items with quantities, prices, and discounts
   - Include order history/tracking section
   - Show payment status with easy payment marking option
   - Provide status update controls with confirmation
   - Show related customer and dealer information

3. **Order Create/Edit Form**
   - Multi-step form for order creation
   - Dealer selection component
   - Dynamic item selection with inventory availability check
   - Quantity adjustments with real-time totals calculation
   - Discount and pricing controls
   - Shipping and delivery information capture

### Quotation Management Interface

1. **Quotation List View**
   - Display list of quotations with expiration countdown
   - Filter by status (pending, accepted, rejected, expired)
   - Quick convert to order action for accepted quotations

2. **Quotation Create/Edit Form**
   - Similar to order creation but with validity period
   - Item selection with configurable pricing
   - Terms and conditions section

### Device Management Interface

1. **Device Registration and Tracking**
   - Device registration form with serial number validation
   - Customer assignment interface
   - Warranty information display
   - Service history tracking

2. **Device List View**
   - Filterable list with status indicators
   - Warranty expiration warnings
   - Quick access to customer contact information

### Commission Management Interface

1. **Commission Calculation and Tracking**
   - Commission calculation based on order value
   - Commission summary by dealer
   - Commission payment tracking

## Data Models

### Order Model

```typescript
interface Order {
  id: string;
  order_number: string;
  dealer_id: string;
  order_date: string;
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  is_paid: boolean;
  shipping_address?: string;
  shipping_date?: string;
  delivery_date?: string;
  completion_date?: string;
  total_price: number;
  vat_amount: number;
  grand_total: number;
  currency: 'try' | 'usd' | 'eur';
  device_set_count: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}
```

### OrderItem Model

```typescript
interface OrderItem {
  id: string;
  order_id: string;
  item_id: string;
  quantity: number;
  unit_price: number;
  discount_percentage: number;
  dealer_discount_percentage: number;
  discounted_price: number;
  vat_percentage: number;
  vat_amount: number;
  total_price: number;
  created_at: string;
  updated_at: string;
}
```

### Quotation Model

```typescript
interface Quotation {
  id: string;
  quotation_number: string;
  dealer_id: string;
  customer_id: string;
  issue_date: string;
  valid_until: string;
  status: 'pending' | 'accepted' | 'rejected' | 'expired';
  total_price: number;
  vat_amount: number;
  grand_total: number;
  currency: 'try' | 'usd' | 'eur';
  notes?: string;
  created_at: string;
  updated_at: string;
}
```

### Device Model

```typescript
interface Device {
  id: string;
  serial_number: string;
  model: string;
  customer_id: string;
  dealer_id: string;
  order_id?: string;
  registration_date: string;
  warranty_start_date: string;
  warranty_end_date: string;
  status: 'active' | 'inactive' | 'under_repair' | 'replaced';
  notes?: string;
  created_at: string;
  updated_at: string;
}
```

### Commission Model

```typescript
interface Commission {
  id: string;
  dealer_id: string;
  order_id: string;
  amount: number;
  commission_percentage: number;
  status: 'pending' | 'paid' | 'cancelled';
  payment_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}
```

## Error Handling

- Implement appropriate error handling for all API requests
- Display meaningful error messages to users
- Handle validation errors with clear feedback
- Provide confirmation dialogs for critical actions
- Show loading states during API calls

## Security Considerations

1. **Authorization**
   - Implement role-based access control in UI
   - Hide sensitive pricing information based on user role
   - Ensure proper access control for sales management functions

2. **Form Security**
   - Implement proper input validation
   - Sanitize inputs to prevent XSS attacks
   - Verify pricing calculations on the server-side

## UI/UX Recommendations

1. **Sales Dashboard**
   - Overview of recent orders and quotations
   - Sales performance metrics and charts
   - Pending actions and notifications
   - Revenue forecasting

2. **Order Workflow Visualization**
   - Clear status indicators with progress visualization
   - Timeline view of order history
   - Notification system for status changes

3. **Print and Export Functionality**
   - Generate printable order and quotation PDFs
   - Export options for orders and sales data
   - Batch operations for common tasks

4. **Inventory Integration**
   - Real-time inventory levels during order creation
   - Low stock warnings
   - Automatic inventory adjustments on order fulfillment
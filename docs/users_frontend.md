# Users Module - Frontend Implementation Guide

## Overview

The Users module handles user authentication, registration, user management, roles, and departments. It's a core module that provides user management functionality across the SmartEQ platform.

## API Endpoints

### Authentication

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/v1/users/auth/login/` | POST | Log in a user | `{ "username": "string", "password": "string" }` | JWT tokens and user data |
| `/api/v1/users/auth/register/` | POST | Register a new user | `{ "username": "string", "email": "string", "password": "string", ... }` | User data |
| `/api/v1/users/auth/token/` | POST | Get JWT token | `{ "username": "string", "password": "string" }` | Access and refresh tokens |
| `/api/v1/users/auth/token/refresh/` | POST | Refresh JWT token | `{ "refresh": "string" }` | New access token |
| `/api/v1/users/auth/token/verify/` | POST | Verify token validity | `{ "token": "string" }` | Validation status |
| `/api/v1/users/auth/password/change/` | POST | Change user password | `{ "old_password": "string", "new_password": "string" }` | Success message |
| `/api/v1/users/auth/password/reset/` | POST | Request password reset | `{ "email": "string" }` | Success message |
| `/api/v1/users/auth/password/reset/confirm/` | POST | Confirm password reset | `{ "token": "string", "password": "string" }` | Success message |
| `/api/v1/users/me/` | GET | Get current user profile | None | User data |

### Users Management

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/v1/users/users/` | GET | List all users | None | List of users |
| `/api/v1/users/users/` | POST | Create a new user | User object | Created user |
| `/api/v1/users/users/{id}/` | GET | Get user details | None | User details |
| `/api/v1/users/users/{id}/` | PUT | Update a user | User object | Updated user |
| `/api/v1/users/users/{id}/` | DELETE | Delete a user | None | Success message |

### Roles

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/v1/users/roles/` | GET | List all roles | None | List of roles |
| `/api/v1/users/roles/` | POST | Create a new role | Role object | Created role |
| `/api/v1/users/roles/{id}/` | GET | Get role details | None | Role details |
| `/api/v1/users/roles/{id}/` | PUT | Update a role | Role object | Updated role |
| `/api/v1/users/roles/{id}/` | DELETE | Delete a role | None | Success message |

### Departments

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/v1/users/departments/` | GET | List all departments | None | List of departments |
| `/api/v1/users/departments/` | POST | Create a new department | Department object | Created department |
| `/api/v1/users/departments/{id}/` | GET | Get department details | None | Department details |
| `/api/v1/users/departments/{id}/` | PUT | Update a department | Department object | Updated department |
| `/api/v1/users/departments/{id}/` | DELETE | Delete a department | None | Success message |

## Frontend Implementation Guidelines

### Authentication Flow

1. **Login Process**
   - Implement a login form with username/email and password fields
   - Submit credentials to `/api/v1/users/auth/login/` 
   - Store returned JWT tokens securely (localStorage, sessionStorage, or cookies)
   - Set the access token in the Authorization header for subsequent requests: `Authorization: Bearer {access_token}`
   - Implement token refresh logic using the refresh token when access token expires

2. **Registration Process**
   - Create registration form with required fields
   - Submit to `/api/v1/users/auth/register/`
   - Redirect to login or automatically log in user after successful registration

3. **Password Management**
   - Implement password change functionality for authenticated users
   - Create password reset request and confirmation workflows

### User Management Interface

1. **User List View**
   - Display paginated list of users with search/filter options
   - Show key attributes like name, email, role, department
   - Include actions for view, edit, delete based on user permissions

2. **User Detail View**
   - Show comprehensive user information
   - Include sections for personal details, role assignments, permissions

3. **User Create/Edit Form**
   - Form with fields for all user attributes
   - Role and department selection via dropdowns
   - Permission management interface

### Role and Department Management

1. **Role Management Interface**
   - CRUD operations for roles with permission assignment
   - List view with role details and assigned permissions

2. **Department Management Interface**
   - CRUD operations for departments
   - Organization structure visualization if applicable

## Data Models

### User Model

```typescript
interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  department?: number;
  role?: number;
  date_joined: string;
  last_login?: string;
}
```

### Role Model

```typescript
interface Role {
  id: number;
  name: string;
  description?: string;
  permissions: number[];
}
```

### Department Model

```typescript
interface Department {
  id: number;
  name: string;
  description?: string;
  parent?: number;
}
```

## Error Handling

- Implement appropriate error handling for all API requests
- Display meaningful error messages to users
- Handle authentication errors by redirecting to login page
- Handle authorization errors with appropriate messaging

## Security Considerations

1. **Token Security**
   - Store JWT tokens securely
   - Implement proper token refresh mechanism
   - Clear tokens on logout

2. **Authorization**
   - Implement role-based access control in UI
   - Hide UI elements based on user permissions
   - Validate permissions on the client side but always rely on server-side validation

3. **Form Security**
   - Implement proper input validation
   - Protect against XSS and CSRF attacks

## UI/UX Recommendations

1. **Authentication Screens**
   - Clean, simple login and registration forms
   - Clear error messaging
   - Password strength indicators on registration
   - "Forgot password" workflow

2. **User Management**
   - Sortable and filterable user lists
   - Batch actions for user management
   - Clear permission visualization
   - Role-based access control indicators
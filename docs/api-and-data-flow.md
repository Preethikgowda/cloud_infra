# API And Data Flow

This document explains how the frontend talks to the backend and how data moves through IntelliWealth.

## Base URLs

When running locally with Docker Compose:

```text
Frontend:          http://localhost:3000
Portfolio Service: http://localhost:8000
Market Service:    http://localhost:8001
AI Service:        http://localhost:8002
```

The frontend uses:

```text
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Authentication Flow

### Register

Endpoint:

```http
POST /api/v1/auth/register
```

Request:

```json
{
  "name": "Example User",
  "email": "user@example.com",
  "password": "password123"
}
```

Behavior:

- Creates a new customer in PostgreSQL.
- Always assigns the role `investor`.
- Does not allow public signup as `admin`.

### Login

Endpoint:

```http
POST /api/v1/auth/login
```

Request:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "name": "Example User",
    "email": "user@example.com",
    "role": "investor",
    "is_active": true
  }
}
```

The frontend stores the token in browser local storage and sends it in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

## Customer APIs

### List Customers

Endpoint:

```http
GET /api/v1/customers
```

Access:

```text
Admin only
```

Used by:

```text
Admin page
```

### Create Customer

Endpoint:

```http
POST /api/v1/customers
```

Access:

```text
Admin only
```

Used by:

```text
Admin Add User form
```

### Update Customer

Endpoint:

```http
PUT /api/v1/customers/{customer_id}
```

Access:

- Admin can update users.
- Normal users can update their own profile.
- Normal users cannot change role or active status.

Used by:

- Profile page
- Admin edit user form

## Portfolio APIs

### List Current User Portfolios

Endpoint:

```http
GET /api/v1/portfolio
```

Used by:

- Dashboard
- Portfolio page
- Allocation page
- History page

### Create Portfolio

Endpoint:

```http
POST /api/v1/portfolio
```

Request:

```json
{
  "customer_id": "...",
  "name": "Default Portfolio"
}
```

Normal users can only create portfolios for themselves.

### Add Asset

Endpoint:

```http
POST /api/v1/portfolio/add-asset
```

Request:

```json
{
  "portfolio_id": "...",
  "asset_name": "Apple Inc.",
  "asset_type": "stocks",
  "quantity": 10,
  "purchase_price": 180
}
```

Behavior:

- Creates an asset row.
- Creates a buy transaction.
- Recalculates portfolio total value.

### Remove Asset

Endpoint:

```http
DELETE /api/v1/portfolio/remove-asset/{asset_id}
```

Behavior:

- Removes the asset.
- Recalculates portfolio total value.

### Allocation

Endpoint:

```http
GET /api/v1/portfolio/allocation/{portfolio_id}
```

Behavior:

- Reads assets.
- Groups values by asset type.
- Returns allocation percentages.

### Portfolio History

Endpoint:

```http
GET /api/v1/portfolio/history/{portfolio_id}
```

Returns saved portfolio history snapshots.

### Record Snapshot

Endpoint:

```http
POST /api/v1/portfolio/history/{portfolio_id}/snapshot
```

Behavior:

- Reads the current portfolio total value.
- Saves it to `portfolio_history`.

## Frontend Pages And Backend Usage

| Page | Backend Usage |
|---|---|
| Login | `/auth/login`, `/auth/register` |
| Dashboard | `/portfolio` |
| Portfolio | `/portfolio`, `/portfolio/add-asset`, `/portfolio/remove-asset/{id}` |
| Allocation | `/portfolio` |
| History | `/portfolio`, `/portfolio/history/{id}`, `/portfolio/history/{id}/snapshot` |
| Profile | `/customers/{id}` |
| Admin | `/customers` |

## Security Model

- JWT protects authenticated endpoints.
- Admin-only routes use role checks.
- Users cannot update another user's profile.
- Users cannot create portfolios for other users.
- Users cannot manage assets in portfolios they do not own.
- PostgreSQL security is private in the AWS infrastructure design.

# API Contracts

## Response Envelope

All responses follow this structure:

```json
{
  "data": {},
  "meta": {
    "request_id": "uuid"
  },
  "errors": [
    {
      "code": "string",
      "message": "string",
      "field": "string (optional)"
    }
  ]
}
```

## Base URL

`/api/v1/`

---

## Health Check

### `GET /api/v1/health`
Returns service health status.

**Response:**
```json
{
  "data": {
    "status": "healthy",
    "database": "connected",
    "redis": "connected"
  },
  "meta": { "request_id": "uuid" },
  "errors": []
}
```

---

## Authentication

### `POST /api/v1/auth/register`
Register a new user under a specific tenant.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "string",
  "display_name": "string",
  "tenant_slug": "string"
}
```

**Response:** `{ data: TokenResponse, meta, errors }`

### `POST /api/v1/auth/login`
Authenticate with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "string",
  "tenant_slug": "string (optional)"
}
```

**Response:** `{ data: TokenResponse, meta, errors }`

**Error:** 401 "Invalid credentials" (same for wrong email or password)

### `POST /api/v1/auth/refresh`
Refresh an access token.

**Request:**
```json
{
  "refresh_token": "string"
}
```

**Response:** `{ data: TokenResponse, meta, errors }`

### TokenResponse
```json
{
  "access_token": "jwt-string",
  "refresh_token": "jwt-string",
  "token_type": "bearer"
}
```

### JWT Claims (Access Token)
```json
{
  "sub": "user_id (UUID)",
  "tenant_id": "UUID",
  "role": "admin|manager|viewer",
  "iat": "timestamp",
  "exp": "timestamp (iat + 15min)",
  "type": "access"
}
```

### JWT Claims (Refresh Token)
```json
{
  "sub": "user_id (UUID)",
  "iat": "timestamp",
  "exp": "timestamp (iat + 7days)",
  "type": "refresh"
}
```

---

## Risks

### `POST /api/v1/risks`
Create a new risk in the current tenant's register.

**Request:**
```json
{
  "title": "string",
  "description": "string",
  "threat_source": "string",
  "vulnerability": "string",
  "asset_at_risk": "string",
  "category": "Organisational | People | Physical | Technological",
  "likelihood": 1-5,
  "impact": 1-5,
  "risk_owner_id": "uuid (optional)"
}
```

**Response:** `{ data: RiskResponse, meta, errors }`

### `GET /api/v1/risks`
List risks with cursor pagination.

**Query Parameters:**
- `limit` (default: 50)
- `cursor` (optional)
- `status` (optional)
- `category` (optional)
- `min_score` (optional)
- `max_score` (optional)
- `sort_by` (inherent_risk_score, created_at, updated_at)
- `sort_desc` (boolean)

**Response:**
```json
{
  "data": {
    "items": [RiskResponse, ...],
    "next_cursor": "string | null",
    "has_more": boolean
  },
  "meta": { "request_id": "uuid" },
  "errors": []
}
```

### `GET /api/v1/risks/{id}`
Retrieve a specific risk.

**Response:** `{ data: RiskResponse, meta, errors }`

### `PUT /api/v1/risks/{id}`
Update a specific risk.

**Request:** (Partial Risk payload)

**Response:** `{ data: RiskResponse, meta, errors }`

### `DELETE /api/v1/risks/{id}`
Delete a specific risk.

**Response:** `{ data: null, meta, errors }`

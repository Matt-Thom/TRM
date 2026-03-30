# API Contracts

All API endpoints: method, path, request/response schemas.

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

(Endpoint definitions will be added as they are implemented.)

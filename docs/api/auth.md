# Authentication API

## Overview
Handles JWT token generation and verification

```http
POST /auth/token
Content-Type: application/json

{
  "username": "admin",  
  "password": "secret"
}
```

## Endpoints

### `POST /auth/token`
Generates a JWT access token

**Parameters**:
- `username` (string): Admin username
- `password` (string): Admin password  

**Responses**:
- 200: Returns access token
- 401: Unauthorized

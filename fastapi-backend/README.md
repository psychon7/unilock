# Unilock Identity Platform - FastAPI Backend

## Security Implementation

### Authentication Flow

1. **Token Acquisition**:
   ```http
   POST /auth/token
   ```
   Returns a JWT token with user claims and scopes.

2. **Protected Routes**:
   Include the token in Authorization header:
   ```
   Authorization: Bearer <your-token>
   ```

### API Endpoints

#### Auth Endpoints

| Endpoint | Method | Description | Required Scope |
|----------|--------|-------------|----------------|
| `/auth/token` | POST | Get access token | None |
| `/auth/test-admin` | GET | Test admin endpoint | admin |
| `/auth/test-user` | GET | Test user endpoint | user |

#### Protected Endpoints

Domain management endpoints (all under `/api/v1/domains`) require `admin` scope.

### Configuration

Set these environment variables:
```bash
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Usage Examples

1. Get a token:
```bash
curl -X POST http://localhost:8000/auth/token
```

2. Access protected endpoint:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/domains
```

## Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env` file

3. Run the server:
```bash
uvicorn app.main:app --reload
```

## Testing

Test the security implementation:
1. Get token from `/auth/token`
2. Try accessing protected endpoints with/without token
3. Verify role-based access works

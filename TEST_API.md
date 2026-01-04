# API Testing Guide

## Test the Backend is Running

Open http://localhost:5000 in your browser. You should see:
```json
{
  "message": "AI-Powered Personal Finance Tracker API",
  "status": "running"
}
```

## Test User Registration (No Auth Required)

Open a new terminal and run:

```bash
curl -X POST http://localhost:5000/api/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"password123\"}"
```

Expected response:
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "..."
  }
}
```

## Test User Login

```bash
curl -X POST http://localhost:5000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"testuser\",\"password\":\"password123\"}"
```

Expected response (copy the access_token):
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}
```

## Test Protected Endpoint (Expenses)

Replace `YOUR_TOKEN` with the access_token from login:

```bash
curl -X GET http://localhost:5000/api/expenses/ ^
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
{
  "expenses": []
}
```

## Common Issues

### 422 Error
- Missing or invalid JWT token
- Check that you're sending the Authorization header
- Make sure the token hasn't expired

### 401 Error
- Invalid credentials
- Wrong username or password

### 400 Error
- Missing required fields in request body
- Invalid data format

## Frontend Testing

The 422 errors you're seeing suggest the frontend is trying to access protected routes without a valid token.

**Steps to debug:**

1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for errors related to authentication
4. Check the Network tab to see the actual requests being made
5. Verify that the Authorization header is being sent with requests

**Common Frontend Issues:**

- User not logged in (token not in localStorage)
- Token expired
- API URL mismatch (check that frontend is pointing to http://localhost:5000)

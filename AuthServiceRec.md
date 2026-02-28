## User Authentication Service API Specification

### 1. Register User
**POST** `/auth/register`

**Request Body:**
```
{
  "username": "alice1234",
  "password": "password_in_plaintext"
}
```

**Response:**
```
{
  "user_id": "uuid"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input, missing fields, or username already exists.

---

### 2. User Login
**POST** `/auth/login`

**Request Body:**
```
{
  "username": "alice1234",
  "password": "password_in_plaintext"
}
```

**Response:**
```
{
  "access_token": "<JWT>",
  "expires_in": 3600
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials.

---

### 3. Validate Token
**POST** `/auth/validate`

**Request Body:**
```
{
  "access_token": "<JWT>"
}
```

**Response:**
```
{
  "valid": true,
  "username": "alice1234"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or expired token.
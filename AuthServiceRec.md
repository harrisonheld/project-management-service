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
  "user_id": "<user_id>"  # This is a 24-character hex string ObjectId from MongoDB
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
  "expires_in": 3600,
  "user_id": "<user_id>"
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
  "user_id": "<user_id>",
  "username": "alice1234"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or expired token.

---

**General Notes**
- All endpoints return JSON.
- JWT tokens should be used for authentication between services.
- Passwords must be securely hashed and never returned in responses.
- The ProjectManagement service will call `/auth/validate` to authenticate users and extract user info from tokens.
- The `user_id` returned by the Auth service is a unique, stable identifier (e.g., a MongoDB ObjectId string) and must be used as the user identifier in all ProjectManagement service operations and database records.

## Example Usage in ProjectManagement Service
1. On user action, forward credentials to `/auth/login` and store the returned JWT and user_id.
2. For protected endpoints, require the client to provide the JWT. Validate it by calling `/auth/validate`.
3. Use the returned user_id for all user-related operations and database lookups.
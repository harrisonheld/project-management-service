## Hardware Management Service API Specification

### 1. List Hardware
**GET** `/hardware`

**Response:**
```json
[
  {
    "hardware_id": "507f1f77bcf86cd799439011",
    "name": "Raspberry Pi",
    "description": "A small computer",
    "quantity": 10,
    "capacity": 100
  },
  {
    "hardware_id": "5f2b5c1e1c9d440000a1b2c3",
    "name": "Baby Oil",
    "description": "50 Gallon drum of baby oil",
    "quantity": 500000,
    "capacity": 100
  }
]
```

---

### 2. Get Hardware Details
**GET** `/hardware/<hardware_id>`

**Response:**
On success:
```json
{
  "hardware_id": "507f1f77bcf86cd799439011",
  "name": "Raspberry Pi",
  "description": "A small computer",
  "quantity": 10,
  "capacity": 100
}
```
On failure:
```json
{
  "error": "Human readable reason here"
}
```

**Error Responses:**
- `404 Not Found` - Hardware not found.

---

### 3. Checkout Hardware
**POST** `/hardware/checkout`

**Request Body:**
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "hardware_id": "507f1f77bcf86cd799439011",
  "quantity": 2
}
```


**Response:**
On success:
```json
{
  "success": true,
  "message": "Checked out 2 Raspberry Pi"
}
```
On failure:
```json
{
  "error": "Human readable reason here"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input, missing fields, or not enough hardware available.

---

### 4. Return Hardware
**POST** `/hardware/return`

**Request Body:**
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "hardware_id": "507f1f77bcf86cd799439011",
  "quantity": 1
}
```


**Response:**
On success:
```json
{
  "success": true,
  "message": "Returned 1 Raspberry Pi"
}
```
On failure:
```json
{
  "error": "Human readable reason here"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input, missing fields, or invalid return.

---

**General Notes**
- All endpoints return JSON.
- The HardwareService is the sole authority for hardware inventory, checkout, and return.
- ProjectManagement service must call HardwareService for all hardware operations.
- HardwareService will validate user_id and hardware_id.

## Hardware Management Service API Specification

### 1. List Hardware
**GET** `/hardware`

**Response:**
```
[
  {
    "hardware_id": "uuid",
    "name": "Raspberry Pi",
    "description": "A small computer",
    "quantity": 10
  }
]
```

---

### 2. Get Hardware Details
**GET** `/hardware/<hardware_id>`

**Response:**
```
{
  "hardware_id": "uuid",
  "name": "Raspberry Pi",
  "description": "A small computer",
  "quantity": 10
}
```

---

### 3. Checkout Hardware
**POST** `/hardware/checkout`

**Request Body:**
```
{
  "user_id": "uuid",
  "hardware_id": "uuid",
  "quantity": 2
}
```

**Response:**
```
{
  "success": true,
  "message": "Checked out 2 Raspberry Pi"
}
```

---

### 4. Return Hardware
**POST** `/hardware/return`

**Request Body:**
```
{
  "user_id": "uuid",
  "hardware_id": "uuid",
  "quantity": 1
}
```

**Response:**
```
{
  "success": true,
  "message": "Returned 1 Raspberry Pi"
}
```

---

**General Notes**
- All endpoints return JSON.
- The HardwareService is the sole authority for hardware inventory, checkout, and return.
- ProjectManagement service must call HardwareService for all hardware operations.
- HardwareService will validate user_id and hardware_id.

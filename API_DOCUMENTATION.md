# Web Store API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_token>
```

---

## 1. Authentication Endpoints

### 1.1 Register User
**POST** `/auth/register`

**Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "password123",
    "role": "simple_user"
}
```

**Response:** `201 Created`
```json
{
    "message": "User created successfully",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "role": "simple_user"
    }
}
```

### 1.2 Login
**POST** `/auth/login`

**Body:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response:** `200 OK`
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 1,
        "username": "admin",
        "role": "admin"
    }
}
```

---

## 2. Product Endpoints

### 2.1 Get All Products
**GET** `/products`

**Response:** `200 OK`
```json
[
    {
        "id": 1,
        "name": "Nike Air Max T-Shirt",
        "price": 29.99,
        "discount_percentage": 10,
        "discounted_price": 26.99,
        "gender": "Men",
        "current_quantity": 98,
        "in_stock": true,
        "category": {"id": 1, "name": "Shirts"},
        "brand": {"id": 1, "name": "Nike"},
        "sizes": [{"id": 2, "name": "S"}, {"id": 3, "name": "M"}],
        "colors": [{"id": 1, "name": "Black"}]
    }
]
```

### 2.2 Get Single Product
**GET** `/products/{id}`

### 2.3 Create Product
**POST** `/products`
**Auth Required:** Yes

**Body:**
```json
{
    "name": "New Product",
    "description": "Product description",
    "price": 49.99,
    "gender": "Women",
    "initial_quantity": 100,
    "category_id": 1,
    "brand_id": 1,
    "size_ids": [2, 3, 4],
    "color_ids": [1, 2]
}
```

### 2.4 Update Product
**PUT** `/products/{id}`
**Auth Required:** Yes

### 2.5 Delete Product
**DELETE** `/products/{id}`
**Auth Required:** Yes

### 2.6 Apply Discount
**PATCH** `/products/{id}/discount`
**Auth Required:** Yes

**Body:**
```json
{
    "discount_percentage": 15
}
```

### 2.7 Get Product Quantity (Real-time)
**GET** `/products/{id}/quantity`

**Response:** `200 OK`
```json
{
    "product_id": 1,
    "name": "Nike Air Max T-Shirt",
    "initial_quantity": 100,
    "sold_quantity": 2,
    "current_quantity": 98,
    "in_stock": true
}
```

### 2.8 Advanced Search
**GET** `/products/search`

**Query Parameters:**
- `gender` - Filter by gender (Men, Women, Children)
- `category` - Filter by category name
- `brand` - Filter by brand name
- `price_min` - Minimum price
- `price_max` - Maximum price
- `size` - Filter by size
- `color` - Filter by color
- `availability` - Filter by stock (in_stock, out_of_stock)

**Example:**
```
GET /products/search?gender=women&brand=Nike&size=M&price_min=20&price_max=100
```

---

## 3. Category, Brand, Size, Color Endpoints

### Categories
- **GET** `/products/categories` - Get all categories
- **POST** `/products/categories` - Create category (Auth required)

### Brands
- **GET** `/products/brands` - Get all brands
- **POST** `/products/brands` - Create brand (Auth required)

### Sizes
- **GET** `/products/sizes` - Get all sizes
- **POST** `/products/sizes` - Create size (Auth required)

### Colors
- **GET** `/products/colors` - Get all colors
- **POST** `/products/colors` - Create color (Auth required)

---

## 4. Order Endpoints

### 4.1 Get All Orders
**GET** `/orders`
**Auth Required:** Yes (Admin/Advanced User)

### 4.2 Get Single Order
**GET** `/orders/{id}`
**Auth Required:** Yes

### 4.3 Create Order
**POST** `/orders`

**Body:**
```json
{
    "client": {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "address": "123 Main St, City"
    },
    "items": [
        {
            "product_id": 1,
            "quantity": 2
        },
        {
            "product_id": 3,
            "quantity": 1
        }
    ]
}
```

**Response:** `201 Created`
```json
{
    "message": "Order created successfully",
    "order": {
        "id": 1,
        "status": "pending",
        "total_amount": 253.97,
        "client": {...},
        "items": [...]
    }
}
```

### 4.4 Update Order Status
**PATCH** `/orders/{id}/status`
**Auth Required:** Yes (Admin/Advanced User)

**Body:**
```json
{
    "status": "confirmed"
}
```

**Valid statuses:** `pending`, `confirmed`, `shipped`, `delivered`, `cancelled`

### 4.5 Delete Order
**DELETE** `/orders/{id}`
**Auth Required:** Yes (Admin only)

### 4.6 Get Client Orders
**GET** `/orders/client/{email}`

---

## 5. Report Endpoints
**Auth Required:** Yes (Admin/Advanced User)

### 5.1 Daily Earnings
**GET** `/reports/earnings/daily?date=2024-11-23`

**Response:**
```json
{
    "date": "2024-11-23",
    "total_earnings": 450.50,
    "total_orders": 12,
    "orders": [...]
}
```

### 5.2 Monthly Earnings
**GET** `/reports/earnings/monthly?year=2024&month=11`

**Response:**
```json
{
    "year": 2024,
    "month": 11,
    "total_earnings": 12450.75,
    "total_orders": 156,
    "daily_breakdown": {...}
}
```

### 5.3 Earnings by Date Range
**GET** `/reports/earnings/range?start_date=2024-11-01&end_date=2024-11-23`

### 5.4 Top Selling Products
**GET** `/reports/top-selling-products?limit=10`

**Response:**
```json
{
    "top_products": [
        {
            "product_id": 1,
            "product_name": "Nike Air Max T-Shirt",
            "total_sold": 45,
            "total_revenue": 1214.55
        }
    ]
}
```

### 5.5 Sales by Category
**GET** `/reports/sales-by-category`

### 5.6 Sales by Brand
**GET** `/reports/sales-by-brand`

### 5.7 Order Status Summary
**GET** `/reports/order-status-summary`

---

## 6. User Management Endpoints
**Auth Required:** Yes (Admin only)

### 6.1 Get All Users
**GET** `/users`

### 6.2 Get Single User
**GET** `/users/{id}`

### 6.3 Update User
**PUT** `/users/{id}`

### 6.4 Delete User
**DELETE** `/users/{id}`

---

## User Roles & Permissions

### Admin
- Full access to all endpoints
- Can manage users, products, orders
- Can generate all reports
- Can delete orders

### Advanced User
- Can manage products
- Can view and update orders
- Can generate reports
- Cannot manage users or delete orders

### Simple User
- Can manage products
- Limited access to orders
- Cannot generate reports
- Cannot manage users

---

## Error Responses

### 400 Bad Request
```json
{
    "error": "Missing required fields"
}
```

### 401 Unauthorized
```json
{
    "error": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
    "error": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
    "error": "Product not found"
}
```

---

## Testing Examples

### Using cURL:
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get products
curl http://localhost:5000/api/products

# Search products
curl "http://localhost:5000/api/products/search?gender=Men&price_max=100"

# Create order
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"client":{"name":"John","email":"john@example.com"},"items":[{"product_id":1,"quantity":2}]}'
```

### Using Postman/Thunder Client:
Import this collection or manually create requests for each endpoint.
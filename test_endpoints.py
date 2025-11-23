import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_response(response, title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_api():
    print("\n🚀 Starting API Tests...\n")
    
    # Test 1: Server is running
    print("\n1️⃣ Testing if server is running...")
    try:
        response = requests.get("http://localhost:5000/")
        print_response(response, "Server Status")
    except Exception as e:
        print(f"❌ Server is not running! Error: {e}")
        print("Please run: python run.py")
        return
    
    # Test 2: Login as admin
    print("\n2️⃣ Testing login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response(response, "Admin Login")
    
    if response.status_code == 200:
        token = response.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        print(f"\n✅ Token obtained: {token[:50]}...")
    else:
        print("\n❌ Login failed!")
        return
    
    # Test 3: Get all products
    print("\n3️⃣ Testing get all products...")
    response = requests.get(f"{BASE_URL}/products")
    print_response(response, "Get All Products")
    
    # Test 4: Advanced search
    print("\n4️⃣ Testing advanced search...")
    response = requests.get(f"{BASE_URL}/products/search?gender=Men&price_max=100")
    print_response(response, "Advanced Search")
    
    # Test 5: Get product quantity
    print("\n5️⃣ Testing product quantity API...")
    response = requests.get(f"{BASE_URL}/products/1/quantity")
    print_response(response, "Product Quantity")
    
    # Test 6: Create an order
    print("\n6️⃣ Testing create order...")
    order_data = {
        "client": {
            "name": "Test Customer",
            "email": "test@example.com",
            "phone": "1234567890",
            "address": "123 Test St"
        },
        "items": [
            {
                "product_id": 1,
                "quantity": 2
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print_response(response, "Create Order")
    
    # Test 7: Get daily earnings (requires admin token)
    print("\n7️⃣ Testing daily earnings report...")
    response = requests.get(f"{BASE_URL}/reports/earnings/daily", headers=headers)
    print_response(response, "Daily Earnings Report")
    
    # Test 8: Get top selling products
    print("\n8️⃣ Testing top selling products...")
    response = requests.get(f"{BASE_URL}/reports/top-selling-products?limit=5", headers=headers)
    print_response(response, "Top Selling Products")
    
    print("\n\n All tests completed!")

if __name__ == "__main__":
    test_api()
import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_response(response, title):
    """Print the response neatly"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except ValueError:
        print(f"Response: {response.text}")

def test_api():
    print("\nStarting API Tests...\n")

    # ------------------ Test 1: Server is running ------------------
    print("1. Testing if server is running...")
    try:
        response = requests.get("http://localhost:5000/")
        print_response(response, "Server Status")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Server is not running! Error: {e}")
        print("Please run: python run.py")
        return

    # ------------------ Test 2: Login as admin ------------------
    print("2. Testing login...")
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response(response, "Admin Login")

    if response.status_code == 200:
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Token obtained: {token[:50]}...")
    else:
        print("Login failed!")
        return

    # ------------------ Test 3: Get all products ------------------
    print("3. Testing get all products...")
    response = requests.get(f"{BASE_URL}/products")
    print_response(response, "Get All Products")

    # ------------------ Test 4: Advanced search ------------------
    print("4. Testing advanced search...")
    response = requests.get(f"{BASE_URL}/products/search?gender=Men&price_max=100")
    print_response(response, "Advanced Search")

    # ------------------ Test 5: Get product quantity ------------------
    print("5. Testing product quantity API...")
    response = requests.get(f"{BASE_URL}/products/1/quantity")
    print_response(response, "Product Quantity")

    # ------------------ Test 6: Create an order ------------------
    print("6. Testing create order...")
    order_data = {
        "client": {
            "name": "Test Customer",
            "email": "test@example.com",
            "phone": "1234567890",
            "address": "123 Test St"
        },
        "items": [{"product_id": 1, "quantity": 2}]
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print_response(response, "Create Order")

    # ------------------ Test 7: Daily earnings report ------------------
    print("7. Testing daily earnings report...")
    response = requests.get(f"{BASE_URL}/reports/earnings/daily", headers=headers)
    print_response(response, "Daily Earnings Report")

    # ------------------ Test 8: Top selling products ------------------
    print("8. Testing top selling products...")
    response = requests.get(f"{BASE_URL}/reports/top-selling-products?limit=5", headers=headers)
    print_response(response, "Top Selling Products")

    print("\nAll tests completed!")

# Run the tests if this file is executed
if __name__ == "__main__":
    test_api()
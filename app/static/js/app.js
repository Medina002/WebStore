const API_BASE = '/api';
let token = null;
let currentUser = null;
let cart = [];
let categories = [];
let brands = [];

// ==================== LOGIN ====================
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });

        const data = await response.json();
        
        if (response.ok) {
            token = data.access_token;
            currentUser = data.user;
            document.getElementById('loginPage').classList.add('hidden');
            document.getElementById('mainApp').classList.remove('hidden');
            document.getElementById('displayUsername').textContent = currentUser.username;
            document.getElementById('displayRole').textContent = `Role: ${currentUser.role}`;
            
            // Hide tabs based on role
            if (currentUser.role === 'simple_user') {
                document.getElementById('reportsTab').style.display = 'none';
                document.getElementById('usersTab').style.display = 'none';
            }
            if (currentUser.role !== 'admin') {
                document.getElementById('usersTab').style.display = 'none';
            }
            
            await loadInitialData();
        } else {
            showMessage('loginMessage', data.error, 'error');
        }
    } catch (error) {
        showMessage('loginMessage', 'Login failed: ' + error.message, 'error');
    }
});

function logout() {
    token = null;
    currentUser = null;
    cart = [];
    document.getElementById('loginPage').classList.remove('hidden');
    document.getElementById('mainApp').classList.add('hidden');
    document.getElementById('loginForm').reset();
    updateCartBadge();
}

// ==================== TAB NAVIGATION ====================
function showTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    // Find button that corresponds to this tab and make active
    const buttons = document.querySelectorAll('.tab');
    buttons.forEach(btn => {
        if(btn.getAttribute('onclick').includes(tabName)) {
            btn.classList.add('active');
        }
    });

    document.getElementById(tabName).classList.add('active');

    if (tabName === 'orders') loadOrders();
    if (tabName === 'reports') loadReports();
    if (tabName === 'users') loadUsers();
    if (tabName === 'cart') displayCart();
}

// ==================== INITIAL DATA ====================
async function loadInitialData() {
    await loadCategories();
    await loadBrands();
    await loadProducts();
}

async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/products/categories`);
        categories = await response.json();
        
        const selects = ['searchCategory', 'productCategory'];
        selects.forEach(id => {
            const select = document.getElementById(id);
            select.innerHTML = '<option value="">All Categories</option>';
            categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.name;
                select.appendChild(option);
            });
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadBrands() {
    try {
        const response = await fetch(`${API_BASE}/products/brands`);
        brands = await response.json();
        
        const selects = ['searchBrand', 'productBrand'];
        selects.forEach(id => {
            const select = document.getElementById(id);
            select.innerHTML = '<option value="">All Brands</option>';
            brands.forEach(brand => {
                const option = document.createElement('option');
                option.value = brand.id;
                option.textContent = brand.name;
                select.appendChild(option);
            });
        });
    } catch (error) {
        console.error('Error loading brands:', error);
    }
}

// ==================== PRODUCTS ====================
async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/products`);
        const products = await response.json();
        displayProducts(products, 'productsGrid');
    } catch (error) {
        showMessage('messageContainer', 'Error loading products: ' + error.message, 'error');
    }
}

function displayProducts(products, containerId) {
    const container = document.getElementById(containerId);
    if (products.length === 0) {
        container.innerHTML = '<p>No products found.</p>';
        return;
    }

    container.innerHTML = products.map(product => `
        <div class="product-card">
            ${product.discount_percentage > 0 ? `<div class="badge">${product.discount_percentage}% OFF</div>` : ''}
            <h3>${product.name}</h3>
            <p class="description">${product.description || 'No description'}</p>
            <div class="tags">
                <span class="tag">${product.gender}</span>
                <span class="tag">${product.category?.name || 'N/A'}</span>
                <span class="tag">${product.brand?.name || 'N/A'}</span>
            </div>
            <div class="price">
                ${product.discount_percentage > 0 ? `<span class="original-price">$${product.price.toFixed(2)}</span>` : ''}
                $${product.discounted_price.toFixed(2)}
            </div>
            <div class="stock ${product.in_stock ? 'in-stock' : 'out-of-stock'}">
                ${product.in_stock ? `✓ In Stock (${product.current_quantity})` : '✗ Out of Stock'}
            </div>
            <div class="product-actions">
                ${product.in_stock ? `<button class="btn-small" onclick="addToCart(${product.id}, '${product.name.replace(/'/g, "\\'")}', ${product.discounted_price})">Add to Cart</button>` : ''}
                <button class="btn-small btn-secondary" onclick="viewProductDetails(${product.id})">Details</button>
            </div>
        </div>
    `).join('');
}

async function performSearch() {
    const params = new URLSearchParams();
    const gender = document.getElementById('searchGender').value;
    const categorySelect = document.getElementById('searchCategory');
    const category = categorySelect.value ? categorySelect.options[categorySelect.selectedIndex].text : '';
    
    const brandSelect = document.getElementById('searchBrand');
    const brand = brandSelect.value ? brandSelect.options[brandSelect.selectedIndex].text : '';
    
    const minPrice = document.getElementById('searchMinPrice').value;
    const maxPrice = document.getElementById('searchMaxPrice').value;
    const availability = document.getElementById('searchAvailability').value;

    if (gender) params.append('gender', gender);
    if (category && category !== 'All Categories') params.append('category', category);
    if (brand && brand !== 'All Brands') params.append('brand', brand);
    if (minPrice) params.append('price_min', minPrice);
    if (maxPrice) params.append('price_max', maxPrice);
    if (availability) params.append('availability', availability);

    try {
        const response = await fetch(`${API_BASE}/products/search?${params}`);
        const products = await response.json();
        displayProducts(products, 'searchResults');
        showMessage('messageContainer', `Found ${products.length} products`, 'success');
    } catch (error) {
        showMessage('messageContainer', 'Search failed: ' + error.message, 'error');
    }
}

async function viewProductDetails(productId) {
    try {
        const response = await fetch(`${API_BASE}/products/${productId}/quantity`);
        const data = await response.json();
        // Simple alert for details as per existing code style, consider a modal in future
        alert(`Product Details:\n\nName: ${data.name}\nInitial Quantity: ${data.initial_quantity}\nSold: ${data.sold_quantity}\nAvailable: ${data.current_quantity}\nStatus: ${data.in_stock ? 'In Stock' : 'Out of Stock'}`);
    } catch (error) {
        showMessage('messageContainer', 'Error: ' + error.message, 'error');
    }
}

// ==================== ADD PRODUCT ====================
function showAddProductModal() {
    document.getElementById('addProductModal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

document.getElementById('addProductForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const productData = {
        name: document.getElementById('productName').value,
        description: document.getElementById('productDescription').value,
        price: parseFloat(document.getElementById('productPrice').value),
        discount_percentage: parseFloat(document.getElementById('productDiscount').value),
        gender: document.getElementById('productGender').value,
        initial_quantity: parseInt(document.getElementById('productQuantity').value),
        category_id: parseInt(document.getElementById('productCategory').value),
        brand_id: parseInt(document.getElementById('productBrand').value)
    };

    try {
        const response = await fetch(`${API_BASE}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(productData)
        });

        const data = await response.json();
        
        if (response.ok) {
            showMessage('messageContainer', 'Product added successfully!', 'success');
            closeModal('addProductModal');
            document.getElementById('addProductForm').reset();
            loadProducts();
        } else {
            showMessage('messageContainer', data.error || 'Error adding product', 'error');
        }
    } catch (error) {
        console.error('Error adding product:', error);
        showMessage('messageContainer', 'Failed to add product: ' + error.message, 'error');
    }
});

// ==================== CART LOGIC ====================
function addToCart(productId, name, price) {
    const existingItem = cart.find(item => item.product_id === productId);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ product_id: productId, name: name, price: price, quantity: 1 });
    }
    updateCartBadge();
    showMessage('messageContainer', `${name} added to cart`, 'success');
}

function removeFromCart(index) {
    cart.splice(index, 1);
    updateCartBadge();
    displayCart();
}

function updateCartBadge() {
    const badge = document.getElementById('cartBadge');
    const count = cart.reduce((acc, item) => acc + item.quantity, 0);
    badge.textContent = count;
    if (count > 0) badge.classList.remove('hidden');
    else badge.classList.add('hidden');
}

function displayCart() {
    const container = document.getElementById('cartContent');
    if (cart.length === 0) {
        container.innerHTML = '<p>Your cart is empty.</p>';
        return;
    }

    let total = 0;
    const itemsHtml = cart.map((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        return `
            <div class="cart-item" style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee;">
                <div>
                    <strong>${item.name}</strong>
                    <div>$${item.price.toFixed(2)} x ${item.quantity}</div>
                </div>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <strong>$${itemTotal.toFixed(2)}</strong>
                    <button class="btn-small btn-danger" style="background-color: #dc3545;" onclick="removeFromCart(${index})">Remove</button>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = `
        <div class="cart-list">${itemsHtml}</div>
        <div class="cart-total" style="margin-top: 20px; text-align: right; font-size: 1.2em;">
            <strong>Total: $${total.toFixed(2)}</strong>
        </div>
        <div style="margin-top: 20px; text-align: right;">
            <button class="btn" onclick="checkout()">Checkout</button>
        </div>
    `;
}

async function checkout() {
    if (cart.length === 0) return;
    if (!confirm('Confirm purchase?')) return;

    try {
        const orderData = { items: cart.map(i => ({ product_id: i.product_id, quantity: i.quantity })) };
        const response = await fetch(`${API_BASE}/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(orderData)
        });

        const data = await response.json();
        if (response.ok) {
            cart = [];
            updateCartBadge();
            displayCart();
            showMessage('messageContainer', 'Order placed successfully!', 'success');
            showTab('orders');
        } else {
            showMessage('messageContainer', data.error || 'Checkout failed', 'error');
        }
    } catch (error) {
        showMessage('messageContainer', 'Checkout error: ' + error.message, 'error');
    }
}

// ==================== ORDERS LOGIC ====================
async function loadOrders() {
    const container = document.getElementById('ordersContent');
    container.innerHTML = '<p>Loading orders...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/orders`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const orders = await response.json();

        if (orders.length === 0) {
            container.innerHTML = '<p>No order history.</p>';
            return;
        }

        container.innerHTML = orders.map(order => `
            <div class="order-card" style="border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 6px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <strong>Order #${order.id}</strong>
                    <span>${new Date(order.created_at).toLocaleString()}</span>
                </div>
                <div>Status: <strong>${order.status}</strong></div>
                <div>Total: <strong>$${order.total_price.toFixed(2)}</strong></div>
                <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                    Items: ${order.items ? order.items.length : 'N/A'}
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
    }
}

// ==================== REPORTS LOGIC ====================
async function loadReports() {
    const container = document.getElementById('reportsContent');
    const statsGrid = document.getElementById('statsGrid');
    
    try {
        // Assuming generic analytics endpoint
        const response = await fetch(`${API_BASE}/reports/dashboard`, { // ADJUST IF NEEDED
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if(!response.ok) throw new Error("Failed to load reports");
        const data = await response.json();

        // Render Stats Cards
        statsGrid.innerHTML = `
            <div class="stat-card" style="background:#f8f9fa; padding:15px; border-radius:8px; text-align:center;">
                <h3>$${data.total_revenue || 0}</h3>
                <p>Total Revenue</p>
            </div>
            <div class="stat-card" style="background:#f8f9fa; padding:15px; border-radius:8px; text-align:center;">
                <h3>${data.total_orders || 0}</h3>
                <p>Total Orders</p>
            </div>
            <div class="stat-card" style="background:#f8f9fa; padding:15px; border-radius:8px; text-align:center;">
                <h3>${data.total_users || 0}</h3>
                <p>Users</p>
            </div>
        `;
        
        // Render Detailed Table if data exists
        if (data.top_products) {
            container.innerHTML = `
                <h3>Top Selling Products</h3>
                <table style="width:100%; border-collapse: collapse;">
                    <thead><tr style="background:#eee;"><th style="padding:8px;">Product</th><th style="padding:8px;">Sold</th></tr></thead>
                    <tbody>
                        ${data.top_products.map(p => `<tr><td style="padding:8px; border-bottom:1px solid #eee;">${p.name}</td><td style="padding:8px; border-bottom:1px solid #eee;">${p.sold}</td></tr>`).join('')}
                    </tbody>
                </table>
            `;
        }
    } catch (error) {
        container.innerHTML = '<p>Could not load reports data. Check console.</p>';
        console.error(error);
    }
}

// ==================== USERS LOGIC ====================
async function loadUsers() {
    const container = document.getElementById('usersContent');
    container.innerHTML = '<p>Loading users...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/users`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const users = await response.json();

        container.innerHTML = `
            <table style="width:100%; border-collapse: collapse; margin-top: 10px;">
                <thead>
                    <tr style="background-color: #f2f2f2; text-align: left;">
                        <th style="padding: 10px;">ID</th>
                        <th style="padding: 10px;">Username</th>
                        <th style="padding: 10px;">Role</th>
                        <th style="padding: 10px;">Email</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(u => `
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 10px;">${u.id}</td>
                            <td style="padding: 10px;">${u.username}</td>
                            <td style="padding: 10px;">${u.role}</td>
                            <td style="padding: 10px;">${u.email || '-'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        container.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
    }
}

// ==================== GLOBAL HELPERS ====================
function showMessage(elementId, text, type) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = text;
        el.className = type === 'error' ? 'message error' : 'message success';
        el.style.display = 'block';
        el.style.padding = '10px';
        el.style.margin = '10px 0';
        el.style.borderRadius = '4px';
        el.style.backgroundColor = type === 'error' ? '#f8d7da' : '#d4edda';
        el.style.color = type === 'error' ? '#721c24' : '#155724';
        
        setTimeout(() => { el.style.display = 'none'; }, 3000);
    }
}
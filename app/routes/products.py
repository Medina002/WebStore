from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models import Product, Category, Brand, Size, Color
from sqlalchemy import and_, or_

bp = Blueprint('products', __name__, url_prefix='/api/products')

def require_role(required_roles):
    """Decorator to check user role"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            if user_role not in required_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@bp.route('/', methods=['GET'])
def get_products():
    """Get all products"""
    products = Product.query.all()
    return jsonify([product.to_dict(include_quantity=True) for product in products]), 200

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product by ID"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(product.to_dict(include_quantity=True)), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    """Create a new product (All users can create)"""
    data = request.get_json()
    
    required_fields = ['name', 'price', 'gender', 'initial_quantity', 'category_id', 'brand_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        discount_percentage=data.get('discount_percentage', 0.0),
        gender=data['gender'],
        initial_quantity=data['initial_quantity'],
        category_id=data['category_id'],
        brand_id=data['brand_id']
    )
    
    # Add sizes
    if 'size_ids' in data:
        sizes = Size.query.filter(Size.id.in_(data['size_ids'])).all()
        product.sizes = sizes
    
    # Add colors
    if 'color_ids' in data:
        colors = Color.query.filter(Color.id.in_(data['color_ids'])).all()
        product.colors = colors
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'message': 'Product created successfully',
        'product': product.to_dict()
    }), 201

@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update a product"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'discount_percentage' in data:
        product.discount_percentage = data['discount_percentage']
    if 'gender' in data:
        product.gender = data['gender']
    if 'initial_quantity' in data:
        product.initial_quantity = data['initial_quantity']
    if 'category_id' in data:
        product.category_id = data['category_id']
    if 'brand_id' in data:
        product.brand_id = data['brand_id']
    
    # Update sizes
    if 'size_ids' in data:
        sizes = Size.query.filter(Size.id.in_(data['size_ids'])).all()
        product.sizes = sizes
    
    # Update colors
    if 'color_ids' in data:
        colors = Color.query.filter(Color.id.in_(data['color_ids'])).all()
        product.colors = colors
    
    db.session.commit()
    
    return jsonify({
        'message': 'Product updated successfully',
        'product': product.to_dict()
    }), 200

@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete a product"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'message': 'Product deleted successfully'}), 200

@bp.route('/<int:product_id>/discount', methods=['PATCH'])
@jwt_required()
def apply_discount(product_id):
    """Apply discount to a product"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.get_json()
    if 'discount_percentage' not in data:
        return jsonify({'error': 'Missing discount_percentage'}), 400
    
    product.discount_percentage = data['discount_percentage']
    db.session.commit()
    
    return jsonify({
        'message': 'Discount applied successfully',
        'product': product.to_dict()
    }), 200

@bp.route('/<int:product_id>/quantity', methods=['GET'])
def get_product_quantity(product_id):
    """Get real-time product quantity"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    sold_quantity = db.session.query(db.func.sum(db.text('order_items.quantity')))\
        .select_from(db.text('order_items'))\
        .join(db.text('orders'), db.text('order_items.order_id = orders.id'))\
        .filter(db.text('order_items.product_id = :product_id'))\
        .filter(db.text("orders.status IN ('confirmed', 'shipped', 'delivered')"))\
        .params(product_id=product_id)\
        .scalar() or 0
    
    current_quantity = product.initial_quantity - sold_quantity
    
    return jsonify({
        'product_id': product.id,
        'name': product.name,
        'initial_quantity': product.initial_quantity,
        'sold_quantity': sold_quantity,
        'current_quantity': current_quantity,
        'in_stock': current_quantity > 0
    }), 200

@bp.route('/search', methods=['GET'])
def search_products():
    """Advanced product search with multiple filters"""
    query = Product.query
    
    # Filter by gender
    gender = request.args.get('gender')
    if gender:
        query = query.filter(Product.gender.ilike(f'%{gender}%'))
    
    # Filter by category
    category = request.args.get('category')
    if category:
        query = query.join(Category).filter(Category.name.ilike(f'%{category}%'))
    
    # Filter by brand
    brand = request.args.get('brand')
    if brand:
        query = query.join(Brand).filter(Brand.name.ilike(f'%{brand}%'))
    
    # Filter by price range
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)
    if price_min is not None:
        query = query.filter(Product.price >= price_min)
    if price_max is not None:
        query = query.filter(Product.price <= price_max)
    
    # Filter by size
    size = request.args.get('size')
    if size:
        query = query.join(Product.sizes).filter(Size.name.ilike(f'%{size}%'))
    
    # Filter by color
    color = request.args.get('color')
    if color:
        query = query.join(Product.colors).filter(Color.name.ilike(f'%{color}%'))
    
    # Filter by availability
    availability = request.args.get('availability')
    
    products = query.all()
    
    # Filter by stock if needed
    if availability == 'in_stock':
        products = [p for p in products if p.get_current_quantity() > 0]
    elif availability == 'out_of_stock':
        products = [p for p in products if p.get_current_quantity() <= 0]
    
    return jsonify([product.to_dict(include_quantity=True) for product in products]), 200

# Category Routes
@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    categories = Category.query.all()
    return jsonify([cat.to_dict() for cat in categories]), 200

@bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """Create a new category"""
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing name'}), 400
    
    category = Category(name=data['name'], description=data.get('description', ''))
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category.to_dict()), 201

# Brand Routes
@bp.route('/brands', methods=['GET'])
def get_brands():
    """Get all brands"""
    brands = Brand.query.all()
    return jsonify([brand.to_dict() for brand in brands]), 200

@bp.route('/brands', methods=['POST'])
@jwt_required()
def create_brand():
    """Create a new brand"""
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing name'}), 400
    
    brand = Brand(name=data['name'], description=data.get('description', ''))
    db.session.add(brand)
    db.session.commit()
    
    return jsonify(brand.to_dict()), 201

# Size Routes
@bp.route('/sizes', methods=['GET'])
def get_sizes():
    """Get all sizes"""
    sizes = Size.query.all()
    return jsonify([size.to_dict() for size in sizes]), 200

@bp.route('/sizes', methods=['POST'])
@jwt_required()
def create_size():
    """Create a new size"""
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing name'}), 400
    
    size = Size(name=data['name'])
    db.session.add(size)
    db.session.commit()
    
    return jsonify(size.to_dict()), 201

# Color Routes
@bp.route('/colors', methods=['GET'])
def get_colors():
    """Get all colors"""
    colors = Color.query.all()
    return jsonify([color.to_dict() for color in colors]), 200

@bp.route('/colors', methods=['POST'])
@jwt_required()
def create_color():
    """Create a new color"""
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing name'}), 400
    
    color = Color(name=data['name'], hex_code=data.get('hex_code'))
    db.session.add(color)
    db.session.commit()
    
    return jsonify(color.to_dict()), 201
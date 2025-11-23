from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models import Order, OrderItem, Client, Product

bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """Get all orders (Admin and Advanced users only)"""
    claims = get_jwt()
    role = claims.get('role')
    
    if role not in ['admin', 'advanced_user']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders]), 200

@bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get single order"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify(order.to_dict()), 200

@bp.route('/', methods=['POST'])
def create_order():
    """Create a new order"""
    data = request.get_json()
    
    if not data or not data.get('client') or not data.get('items'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get or create client
    client_data = data['client']
    client = Client.query.filter_by(email=client_data['email']).first()
    
    if not client:
        client = Client(
            name=client_data['name'],
            email=client_data['email'],
            phone=client_data.get('phone'),
            address=client_data.get('address')
        )
        db.session.add(client)
        db.session.flush()
    
    # Calculate total and create order
    total_amount = 0
    order = Order(client_id=client.id, total_amount=0)
    db.session.add(order)
    db.session.flush()
    
    # Add order items
    for item_data in data['items']:
        product = Product.query.get(item_data['product_id'])
        if not product:
            db.session.rollback()
            return jsonify({'error': f'Product {item_data["product_id"]} not found'}), 404
        
        # Check stock availability
        current_quantity = product.get_current_quantity()
        if current_quantity < item_data['quantity']:
            db.session.rollback()
            return jsonify({'error': f'Insufficient stock for {product.name}. Available: {current_quantity}'}), 400
        
        price = product.get_discounted_price()
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item_data['quantity'],
            price_at_purchase=price
        )
        db.session.add(order_item)
        total_amount += price * item_data['quantity']
    
    order.total_amount = total_amount
    db.session.commit()
    
    return jsonify({
        'message': 'Order created successfully',
        'order': order.to_dict()
    }), 201

@bp.route('/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
def update_order_status(order_id):
    """Update order status (Admin and Advanced users only)"""
    claims = get_jwt()
    role = claims.get('role')
    
    if role not in ['admin', 'advanced_user']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Missing status'}), 400
    
    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    if data['status'] not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400
    
    order.status = data['status']
    db.session.commit()
    
    return jsonify({
        'message': 'Order status updated successfully',
        'order': order.to_dict()
    }), 200

@bp.route('/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    """Delete an order (Admin only)"""
    claims = get_jwt()
    role = claims.get('role')
    
    if role != 'admin':
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    db.session.delete(order)
    db.session.commit()
    
    return jsonify({'message': 'Order deleted successfully'}), 200

@bp.route('/client/<string:email>', methods=['GET'])
def get_client_orders(email):
    """Get all orders for a specific client by email"""
    client = Client.query.filter_by(email=email).first()
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    orders = Order.query.filter_by(client_id=client.id).all()
    return jsonify({
        'client': client.to_dict(),
        'orders': [order.to_dict() for order in orders]
    }), 200
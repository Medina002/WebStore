from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models import Order, OrderItem, Product
from sqlalchemy import func, and_
from datetime import datetime, timedelta

bp = Blueprint('reports', __name__, url_prefix='/api/reports')

def require_reports_access():
    """Check if user has access to reports (Admin and Advanced users)"""
    claims = get_jwt()
    role = claims.get('role')
    if role not in ['admin', 'advanced_user']:
        return False
    return True

@bp.route('/earnings/daily', methods=['GET'])
@jwt_required()
def daily_earnings():
    """Get daily earnings report"""
    if not require_reports_access():
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Get date from query params or use today
    date_str = request.args.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    else:
        target_date = datetime.utcnow().date()
    
    # Calculate start and end of day
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())
    
    # Query orders for the day
    orders = Order.query.filter(
        and_(
            Order.created_at >= start_of_day,
            Order.created_at <= end_of_day,
            Order.status.in_(['confirmed', 'shipped', 'delivered'])
        )
    ).all()
    
    total_earnings = sum(order.total_amount for order in orders)
    total_orders = len(orders)
    
    return jsonify({
        'date': target_date.isoformat(),
        'total_earnings': round(total_earnings, 2),
        'total_orders': total_orders,
        'orders': [order.to_dict(include_items=False) for order in orders]
    }), 200

@bp.route('/earnings/monthly', methods=['GET'])
@jwt_required()
def monthly_earnings():
    """Get monthly earnings report"""
    if not require_reports_access():
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Get year and month from query params or use current
    year = request.args.get('year', type=int, default=datetime.utcnow().year)
    month = request.args.get('month', type=int, default=datetime.utcnow().month)
    
    # Validate month
    if month < 1 or month > 12:
        return jsonify({'error': 'Invalid month. Use 1-12'}), 400
    
    # Calculate start and end of month
    start_of_month = datetime(year, month, 1)
    if month == 12:
        end_of_month = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_of_month = datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    # Query orders for the month
    orders = Order.query.filter(
        and_(
            Order.created_at >= start_of_month,
            Order.created_at <= end_of_month,
            Order.status.in_(['confirmed', 'shipped', 'delivered'])
        )
    ).all()
    
    total_earnings = sum(order.total_amount for order in orders)
    total_orders = len(orders)
    
    # Group by day
    daily_breakdown = {}
    for order in orders:
        day = order.created_at.date().isoformat()
        if day not in daily_breakdown:
            daily_breakdown[day] = {'earnings': 0, 'orders': 0}
        daily_breakdown[day]['earnings'] += order.total_amount
        daily_breakdown[day]['orders'] += 1
    
    return jsonify({
        'year': year,
        'month': month,
        'total_earnings': round(total_earnings, 2),
        'total_orders': total_orders,
        'daily_breakdown': daily_breakdown
    }), 200

@bp.route('/earnings/range', methods=['GET'])
@jwt_required()
def earnings_by_range():
    """Get earnings for a date range"""
    if not require_reports_access():
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if not start_date_str or not end_date_str:
        return jsonify({'error': 'Missing start_date or end_date parameters'}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        end_date = datetime.combine(end_date.date(), datetime.max.time())
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    if start_date > end_date:
        return jsonify({'error': 'start_date must be before end_date'}), 400
    
    # Query orders for the range
    orders = Order.query.filter(
        and_(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status.in_(['confirmed', 'shipped', 'delivered'])
        )
    ).all()
    
    total_earnings = sum(order.total_amount for order in orders)
    total_orders = len(orders)
    
    return jsonify({
        'start_date': start_date.date().isoformat(),
        'end_date': end_date.date().isoformat(),
        'total_earnings': round(total_earnings, 2),
        'total_orders': total_orders
    }), 200

@bp.route('/top-selling-products', methods=['GET'])
@jwt_required()
def top_selling_products():
    """Get top selling products"""
    if not require_reports_access():
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    limit = request.args.get('limit', type=int, default=10)
    
    # Query to get top selling products
    top_products = db.session.query(
        Product.id,
        Product.name,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.quantity * OrderItem.price_at_purchase).label('total_revenue')
    ).join(OrderItem, Product.id == OrderItem.product_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .filter(Order.status.in_(['confirmed', 'shipped', 'delivered']))\
     .group_by(Product.id, Product.name)\
     .order_by(func.sum(OrderItem.quantity).desc())\
     .limit(limit)\
     .all()
    
    results = []
    for product in top_products:
        results.append({
            'product_id': product.id,
            'product_name': product.name,
            'total_sold': product.total_sold,
            'total_revenue': round(float(product.total_revenue), 2)
        })
    
    return jsonify({
        'top_products': results,
        'count': len(results)
    }), 200

@bp.route('/sales-by-category', methods=['GET'])
@jwt_required()
def sales_by_category():
    """Get sales breakdown by category"""
    if not require_reports_access():
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    from app.models import Category
    
    # Query sales by category
    category_sales = db.session.query(
        Category.name,
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.quantity * OrderItem.price_at_purchase).label('total_revenue')
    ).join(Product, Category.id == Product.category_id)\
     .join(OrderItem, Product.id == OrderItem.product_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .filter(Order.status.in_(['confirmed', 'shipped', 'delivered']))\
     .group_by(Category.name)\
     .order_by(func.sum(OrderItem.quantity * OrderItem.price_at_purchase).desc())\
     .all()
    
    results = []
    for category in category_sales:
        results.append({
            'category': category.name,
            'total_quantity_sold': category.total_quantity,
            'total_revenue': round(float(category.total_revenue), 2)
        })
    
    return jsonify({
        'sales_by_category': results
    }), 200

@bp.route('/sales-by-brand', methods=['GET'])
@jwt_required()
def sales_by_brand():
    """Get sales breakdown by brand"""
    if not require_reports_access():
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    from app.models import Brand
    
    # Query sales by brand
    brand_sales = db.session.query(
        Brand.name,
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.quantity * OrderItem.price_at_purchase).label('total_revenue')
    ).join(Product, Brand.id == Product.brand_id)\
     .join(OrderItem, Product.id == OrderItem.product_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .filter(Order.status.in_(['confirmed', 'shipped', 'delivered']))\
     .group_by(Brand.name)\
     .order_by(func.sum(OrderItem.quantity * OrderItem.price_at_purchase).desc())\
     .all()
    
    results = []
    for brand in brand_sales:
        results.append({
            'brand': brand.name,
            'total_quantity_sold': brand.total_quantity,
            'total_revenue': round(float(brand.total_revenue), 2)
        })
    
    return jsonify({
        'sales_by_brand': results
    }), 200

@bp.route('/order-status-summary', methods=['GET'])
@jwt_required()
def order_status_summary():
    """Get summary of orders by status"""
    if not require_reports_access():
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Query order counts by status
    status_summary = db.session.query(
        Order.status,
        func.count(Order.id).label('count'),
        func.sum(Order.total_amount).label('total_amount')
    ).group_by(Order.status).all()
    
    results = {}
    for status in status_summary:
        results[status.status] = {
            'count': status.count,
            'total_amount': round(float(status.total_amount), 2)
        }
    
    return jsonify({
        'order_status_summary': results
    }), 200
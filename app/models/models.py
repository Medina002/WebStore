from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

# This will be initialized in __init__.py
from app.extensions import db

# Association tables for many-to-many relationships
product_sizes = Table('product_sizes', db.Model.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('size_id', Integer, ForeignKey('sizes.id'), primary_key=True)
)

product_colors = Table('product_colors', db.Model.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('color_id', Integer, ForeignKey('colors.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='simple_user')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    products = relationship('Product', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class Brand(db.Model):
    __tablename__ = 'brands'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    products = relationship('Product', backref='brand', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class Size(db.Model):
    __tablename__ = 'sizes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Color(db.Model):
    __tablename__ = 'colors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)
    hex_code = Column(String(7))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'hex_code': self.hex_code
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    gender = Column(String(20), nullable=False)
    initial_quantity = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Many-to-many relationships
    sizes = relationship('Size', secondary=product_sizes, lazy='subquery',
                        backref=db.backref('products', lazy=True))
    colors = relationship('Color', secondary=product_colors, lazy='subquery',
                         backref=db.backref('products', lazy=True))
    
    def get_discounted_price(self):
        if self.discount_percentage > 0:
            return round(self.price * (1 - self.discount_percentage / 100), 2)
        return self.price
    
    def get_current_quantity(self):
        """Calculate current quantity by subtracting sold items"""
        from sqlalchemy import func
        sold_quantity = db.session.query(func.sum(OrderItem.quantity))\
            .join(Order)\
            .filter(OrderItem.product_id == self.id)\
            .filter(Order.status.in_(['confirmed', 'shipped', 'delivered']))\
            .scalar() or 0
        return self.initial_quantity - sold_quantity
    
    def to_dict(self, include_quantity=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'discount_percentage': self.discount_percentage,
            'discounted_price': self.get_discounted_price(),
            'gender': self.gender,
            'initial_quantity': self.initial_quantity,
            'category': self.category.to_dict() if self.category else None,
            'brand': self.brand.to_dict() if self.brand else None,
            'sizes': [size.to_dict() for size in self.sizes],
            'colors': [color.to_dict() for color in self.colors],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_quantity:
            data['current_quantity'] = self.get_current_quantity()
            data['in_stock'] = self.get_current_quantity() > 0
        return data

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship('Order', backref='client', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat()
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    status = Column(String(20), nullable=False, default='pending')
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_items=True):
        data = {
            'id': self.id,
            'client': self.client.to_dict() if self.client else None,
            'status': self.status,
            'total_amount': self.total_amount,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)
    
    product = relationship('Product', backref='order_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product': self.product.to_dict() if self.product else None,
            'quantity': self.quantity,
            'price_at_purchase': self.price_at_purchase,
            'subtotal': self.quantity * self.price_at_purchase
        }
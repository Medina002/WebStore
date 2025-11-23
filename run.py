from flask import render_template
from app import create_app
from app.extensions import db
from app.models import User, Category, Brand, Size, Color, Product

app = create_app()

@app.route('/')
def index():
    """Serve the frontend"""
    return render_template('index.html')

@app.route('/api')
def api_info():
    """API information endpoint"""
    return {
        'message': 'Web Store API',
        'version': '1.0',
        'endpoints': {
            'auth': '/api/auth',
            'products': '/api/products',
            'orders': '/api/orders',
            'users': '/api/users',
            'reports': '/api/reports'
        }
    }

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database with sample data"""
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("Creating admin user...")
        admin = User(username='admin', email='admin@webstore.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        print("Creating advanced user...")
        advanced = User(username='advanced', email='advanced@webstore.com', role='advanced_user')
        advanced.set_password('advanced123')
        db.session.add(advanced)
        
        print("Creating simple user...")
        simple = User(username='user', email='user@webstore.com', role='simple_user')
        simple.set_password('user123')
        db.session.add(simple)
        
        print("Creating categories...")
        categories = [
            Category(name='Shirts', description='T-shirts, dress shirts, casual shirts'),
            Category(name='Pants', description='Jeans, trousers, casual pants'),
            Category(name='Jackets', description='Winter jackets, blazers, casual jackets'),
            Category(name='Shoes', description='Sneakers, formal shoes, boots'),
            Category(name='Accessories', description='Belts, hats, bags')
        ]
        db.session.add_all(categories)
        
        print("Creating brands...")
        brands = [
            Brand(name='Nike', description='Athletic wear and sportswear'),
            Brand(name='Adidas', description='Sports and casual clothing'),
            Brand(name='Zara', description='Fashion and trendy clothing'),
            Brand(name='H&M', description='Affordable fashion'),
            Brand(name='Tommy Hilfiger', description='Premium casual wear')
        ]
        db.session.add_all(brands)
        
        print("Creating sizes...")
        sizes = [
            Size(name='XS'),
            Size(name='S'),
            Size(name='M'),
            Size(name='L'),
            Size(name='XL'),
            Size(name='XXL')
        ]
        db.session.add_all(sizes)
        
        print("Creating colors...")
        colors = [
            Color(name='Black', hex_code='#000000'),
            Color(name='White', hex_code='#FFFFFF'),
            Color(name='Red', hex_code='#FF0000'),
            Color(name='Blue', hex_code='#0000FF'),
            Color(name='Green', hex_code='#008000'),
            Color(name='Yellow', hex_code='#FFFF00'),
            Color(name='Gray', hex_code='#808080')
        ]
        db.session.add_all(colors)
        
        db.session.commit()
        
        print("Creating sample products...")
        
        products = [
            Product(
                name='Nike Air Max T-Shirt',
                description='Comfortable cotton t-shirt with Nike logo',
                price=29.99,
                discount_percentage=10,
                gender='Men',
                initial_quantity=100,
                category_id=1,
                brand_id=1
            ),
            Product(
                name='Adidas Classic Jeans',
                description='Denim jeans with classic fit',
                price=79.99,
                gender='Women',
                initial_quantity=50,
                category_id=2,
                brand_id=2
            ),
            Product(
                name='Zara Winter Jacket',
                description='Warm winter jacket for cold weather',
                price=199.99,
                discount_percentage=15,
                gender='Men',
                initial_quantity=30,
                category_id=3,
                brand_id=3
            ),
            Product(
                name='Tommy Hilfiger Polo Shirt',
                description='Premium polo shirt',
                price=59.99,
                gender='Women',
                initial_quantity=75,
                category_id=1,
                brand_id=5
            ),
            Product(
                name='Nike Running Shoes',
                description='Lightweight running shoes',
                price=129.99,
                discount_percentage=20,
                gender='Men',
                initial_quantity=60,
                category_id=4,
                brand_id=1
            )
        ]
        
        # Add sizes and colors to products
        for product in products:
            product.sizes = sizes[1:4]  # S, M, L
            product.colors = colors[0:3]  # Black, White, Red
        
        db.session.add_all(products)
        db.session.commit()
        
        print("\n" + "="*50)
        print("Database initialized successfully!")
        print("="*50)
        print("\nDefault users created:")
        print("  Admin: username=admin, password=admin123")
        print("  Advanced User: username=advanced, password=advanced123")
        print("  Simple User: username=user, password=user123")
        print("\nYou can now run: python run.py")
        print("="*50 + "\n")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
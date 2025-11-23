from flask import Flask
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    from app.extensions import db, jwt
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    with app.app_context():
        from app.routes import auth, products, orders, users, reports
        app.register_blueprint(auth.bp)
        app.register_blueprint(products.bp)
        app.register_blueprint(orders.bp)
        app.register_blueprint(users.bp)
        app.register_blueprint(reports.bp)
        
        # Create tables
        db.create_all()
    
    return app
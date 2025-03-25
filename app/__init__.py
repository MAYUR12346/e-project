# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

# # Initialize extensions
# db = SQLAlchemy()
# migrate = Migrate()

# def create_app():
#     app = Flask(__name__, static_folder='static')
    
#     # Database Configuration
#     app.config['SECRET_KEY'] = 'your_secret_key'
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     # Initialize database and migrations
#     db.init_app(app)
#     migrate.init_app(app, db)

#     with app.app_context():
#         from app import models  # Ensure models are loaded

#         # Import and register Blueprints
#         from app.views import views  
#         app.register_blueprint(views)

#         # 🔹 Create tables if they don’t exist
#         db.create_all()

#     return app

from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.secret_key = "V123@rku"  # Change this to a secure secret key in production

    # Database Configuration
    app.config["DEBUG"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Mail Configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'vkumar080@rku.ac.in'  # Update with your email
    app.config['MAIL_PASSWORD'] = 'oqpj npkl jyxh hijh'     # Update with your app password
    app.config['MAIL_DEFAULT_SENDER'] = 'vkumar080@rku.ac.in'

    db.init_app(app)
    mail.init_app(app)

    # Import routes after db initialization to avoid circular imports
    from app.auth import auth_bp
    from app.admin import admin
    from app.views import views
    # Register blueprints
    app.register_blueprint(views)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin)
    with app.app_context():
        db.create_all()

    return app



from . import db
from datetime import datetime, timezone,timedelta
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=False)
    state = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    approved = db.Column(db.Boolean, default=False)    
    role = db.Column(db.String(10), nullable=False)
    
    def generate_reset_token(self, secret_key):
        """Generate a unique reset token for password reset"""
        serializer = URLSafeTimedSerializer(secret_key)
        self.reset_token = serializer.dumps(self.email, salt='password-reset-salt')
        self.reset_token_expiry = datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
        db.session.commit()
        return self.reset_token
    
    @staticmethod
    def verify_reset_token(token, secret_key):
        """Verify a reset token and return the user if valid"""
        serializer = URLSafeTimedSerializer(secret_key)
        try:
            email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hour expiry
            return User.query.filter_by(email=email).first()
        except (SignatureExpired, BadSignature):
            return None





# Brand Model
class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    logo = db.Column(db.String(200), nullable=True)

    products = db.relationship('Product', backref='brand', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Brand {self.name}>"


# Product Model
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_picture = db.Column(db.String(1000), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(2000), nullable=True)
    color = db.Column(db.String(15))
    rating = db.Column(db.Integer, default=0)
    sale = db.Column(db.Boolean, default=False)
    discount = db.Column(db.Integer, nullable=True, default=0)
    count = db.Column(db.Integer, default=0)

    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # ✅ Now category is a string field


    quantity_size = db.relationship('ProductSize', backref='product', lazy=True, cascade="all, delete-orphan")
    carts = db.relationship('Cart', backref='cart_product', lazy=True, cascade="all, delete-orphan")
    wishlists = db.relationship('Wishlist', backref='wishlist_product', lazy=True, cascade="all, delete-orphan")
    order_items = db.relationship('OrderItem', backref='product', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.product_name}, Price: {self.current_price}, Category: {self.category}>"


# Product Size Model
class ProductSize(db.Model):
    __tablename__ = 'product_sizes'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    size = db.Column(db.String(50), nullable=False, default="No size")
    quantity = db.Column(db.Integer, nullable=False, default=0)


# Cart Model (Each user can have their own cart)
class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<Cart User: {self.user_id}, Product: {self.product_id}, Quantity: {self.quantity}>"


# Wishlist Model
class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    def __repr__(self):
        return f"<Wishlist User: {self.user_id}, Product: {self.product_id}>"


# Order Model
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Pending")  # ('Pending', 'Shipped', 'Delivered', 'Cancelled')
    order_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    delivery_date = db.Column(db.DateTime, nullable=True)

    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    customer_name = db.Column(db.String(100), nullable=False)
    address_line_1 = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    mail = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Order {self.id} - {self.status}>"


# Order Item Model (Items in an order)
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)  # Price at time of purchase
    subtotal = db.Column(db.Float, nullable=False)  # quantity * unit_price

    def __repr__(self):
        return f"<OrderItem Order: {self.order_id}, Product: {self.product_id}, Quantity: {self.quantity}>"

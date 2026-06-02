from . import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    provider_code = db.Column(db.String(50), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    order_id = db.Column(db.String(50), primary_key=True)
    target_id = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    sell_price = db.Column(db.Integer, nullable=False)
    provider_price = db.Column(db.Integer, nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    
    # Status: PENDING, PAID, PROCESSING, SUCCESS, FAILED
    status = db.Column(db.String(20), default='PENDING') 
    
    # JSON untuk menyimpan log (butuh PostgreSQL)
    payment_log = db.Column(db.JSON, nullable=True)
    provider_log = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi agar kita bisa dengan mudah mengambil data produk dari sebuah transaksi
    product = db.relationship('Product', backref='transactions')